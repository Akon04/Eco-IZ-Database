import base64
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin, get_current_root_admin, get_current_user
from app.db.session import get_db
from app.models.admin import EcoCategory, Habit
from app.models.challenge import Challenge, UserChallenge
from app.models.chat import ChatMessage
from app.models.post import Post, PostMedia, PostReport
from app.models.user import Activity, ActivityMedia, User
from app.schemas.admin import (
    AdminActivityDetailResponse,
    AdminMediaResponse,
    AchievementMetricsResponse,
    AchievementResponse,
    AdminActivityMetrics,
    EcoAnalyticsCategoryResponse,
    EcoAnalyticsResponse,
    EcoAnalyticsTopUserResponse,
    AdminIdentityResponse,
    AdminUserActivityResponse,
    AdminUserChallengeResponse,
    AdminUserDetailResponse,
    AdminLoginRequest,
    AdminSessionResponse,
    AdminUserMetrics,
    AdminUserPostResponse,
    AdminUserResponse,
    CategoryMetricsResponse,
    CommunityPostDetailResponse,
    CommunityPostResponse,
    CreateAchievementRequest,
    CreateAdminPostRequest,
    CreateCategoryRequest,
    CreateHabitRequest,
    EcoCategoryResponse,
    HabitMetricsResponse,
    HabitResponse,
    PostMetricsResponse,
    UpdateAchievementRequest,
    UpdateAdminUserRequest,
    UpdateCategoryRequest,
    UpdateHabitRequest,
    UpdatePostRequest,
)
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.bootstrap import BootstrapResponse, UserProfileResponse
from app.schemas.common import ChatRequest, HealthResponse
from app.schemas.mutations import (
    ActivityCreateRequest,
    ActivityMutationResponse,
    ChatEnvelope,
    ChallengeClaimResponse,
    PostCreateRequest,
    PostEnvelope,
    PostReportRequest,
    PostsEnvelope,
)
from app.services.ai import ai_response
from app.services.auth import create_session_token, hash_password, needs_password_rehash, verify_password
from app.services.bootstrap import (
    build_bootstrap,
    serialize_activity,
    serialize_chat_message,
    serialize_post,
    serialize_user,
    serialize_user_challenge,
    visible_posts_for_user,
)
from app.services.seed import assign_challenges_for_user
from app.services.user_progress import recalculate_user_progress

router = APIRouter()

POST_REPORT_REASONS = {
    "Спам или реклама",
    "Странные или опасные действия",
    "Оскорбительный контент",
    "Подозрительный пользователь",
}


def fetch_user_with_relations(db: Session, user_id) -> User:
    stmt = (
        select(User)
        .options(
            selectinload(User.activities).selectinload(Activity.media),
            selectinload(User.posts).selectinload(Post.media),
            selectinload(User.chat_messages),
            selectinload(User.user_challenges).selectinload(UserChallenge.challenge),
        )
        .where(User.id == user_id)
    )
    return db.scalar(stmt)


def parse_uuid(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found.") from exc


def estimate_custom_activity_impact(title: str, note: str) -> tuple[float, int]:
    combined = f"{title} {note}".lower()
    trimmed_note = note.strip()
    points = 4
    co2_saved = 0.12

    if any(keyword in combined for keyword in ("велосип", "пеш", "метро", "автобус", "поезд", "самокат")):
        points += 4
        co2_saved += 0.42
    if any(keyword in combined for keyword in ("сортир", "переработ", "вторсыр", "мусор", "компост")):
        points += 3
        co2_saved += 0.28
    if any(keyword in combined for keyword in ("бутыл", "сумк", "упаков", "пластик", "многораз")):
        points += 2
        co2_saved += 0.16
    if any(keyword in combined for keyword in ("душ", "кран", "вода", "утеч")):
        points += 2
        co2_saved += 0.14
    if any(keyword in combined for keyword in ("свет", "ламп", "электр", "заряд", "энерг")):
        points += 2
        co2_saved += 0.16
    if any(keyword in combined for keyword in ("вместо", "отказ", "замен", "сэконом")):
        points += 2
        co2_saved += 0.1
    if len(trimmed_note) > 90:
        points += 1
        co2_saved += 0.06
    if len(trimmed_note) < 28:
        points = min(points, 6)
        co2_saved = min(co2_saved, 0.22)

    return round(min(co2_saved, 1.1), 2), min(points, 14)


def serialize_admin_identity(user: User) -> AdminIdentityResponse:
    return AdminIdentityResponse(id=str(user.id), email=user.email, username=user.username, role=user.role)


def serialize_admin_user(user: User) -> AdminUserResponse:
    return AdminUserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        isEmailVerified=user.is_email_verified,
        ecoPoints=user.points,
        streakDays=user.streak_days,
        postsCount=len(user.posts),
        createdAt=user.created_at,
        status=user.status,
    )


def serialize_admin_user_detail(user: User) -> AdminUserDetailResponse:
    recent_activities = sorted(user.activities, key=lambda value: value.created_at, reverse=True)[:6]
    recent_posts = sorted(user.posts, key=lambda value: value.created_at, reverse=True)[:6]
    challenge_items = sorted(user.user_challenges, key=lambda value: (value.challenge.reward_points, value.challenge.title))

    return AdminUserDetailResponse(
        **serialize_admin_user(user).model_dump(),
        fullName=user.full_name or user.username,
        level=serialize_user(user).level,
        co2SavedTotal=user.co2_saved_total,
        adminNote=user.admin_note or "",
        recentActivities=[
            AdminUserActivityResponse(
                **serialize_activity(item).model_dump(exclude={"note", "media"}),
                userId=str(user.id),
                username=user.username,
                userEmail=user.email,
                note=item.note or "",
            )
            for item in recent_activities
        ],
        challenges=[
            AdminUserChallengeResponse(**serialize_user_challenge(item).model_dump()) for item in challenge_items
        ],
        recentPosts=[
            AdminUserPostResponse(
                id=str(item.id),
                author=item.author_name,
                content=item.text,
                state=item.moderation_state,
                reportsCount=item.reports_count,
                createdAt=item.created_at,
                mediaCount=len(item.media),
            )
            for item in recent_posts
        ],
    )


def serialize_admin_activity(activity: Activity) -> AdminUserActivityResponse:
    return AdminUserActivityResponse(
        **serialize_activity(activity).model_dump(exclude={"note", "media"}),
        userId=str(activity.user.id),
        username=activity.user.username,
        userEmail=activity.user.email,
        note=activity.note or "",
    )


def serialize_admin_activity_detail(activity: Activity) -> AdminActivityDetailResponse:
    return AdminActivityDetailResponse(
        **serialize_admin_activity(activity).model_dump(),
        media=[AdminMediaResponse(**media.model_dump()) for media in serialize_activity(activity).media],
    )


def serialize_category(category: EcoCategory) -> EcoCategoryResponse:
    return EcoCategoryResponse(
        id=str(category.id),
        name=category.name,
        description=category.description or "",
        color=category.color or "",
        icon=category.icon or "",
    )


def serialize_habit(habit: Habit) -> HabitResponse:
    return HabitResponse(
        id=str(habit.id),
        title=habit.title,
        category=habit.category.name,
        points=habit.points,
        co2Value=habit.co2_value,
        waterValue=habit.water_value,
        energyValue=habit.energy_value,
    )


def serialize_achievement(challenge: Challenge) -> AchievementResponse:
    return AchievementResponse(
        id=str(challenge.id),
        title=challenge.title,
        description=challenge.description,
        icon=challenge.badge_symbol,
        targetValue=challenge.target_count,
        rewardPoints=challenge.reward_points,
    )


def serialize_admin_post(post: Post) -> CommunityPostResponse:
    return CommunityPostResponse(
        id=str(post.id),
        author=post.author_name,
        content=post.text,
        state=post.moderation_state,
        reportsCount=post.reports_count,
        createdAt=post.created_at,
    )


def serialize_admin_post_detail(post: Post) -> CommunityPostDetailResponse:
    reason_counts: dict[str, int] = {}
    for report in post.reports:
        reason_counts[report.reason] = reason_counts.get(report.reason, 0) + 1

    return CommunityPostDetailResponse(
        **serialize_admin_post(post).model_dump(),
        media=[AdminMediaResponse(**media.model_dump()) for media in serialize_post(post).media],
        reportReasons=[
            reason if count == 1 else f"{reason} ({count})"
            for reason, count in sorted(reason_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
    )


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower().strip()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if needs_password_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
    token = create_session_token(db, user)
    return AuthResponse(token=token, user=serialize_user(user))


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.scalar(select(User).where(User.email == payload.email.lower().strip()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists.")

    user = User(
        full_name=payload.fullName.strip(),
        email=payload.email.lower().strip(),
        username=payload.email.split("@")[0].lower().strip(),
        password_hash=hash_password(payload.password),
        role="USER",
        status="ACTIVE",
        is_email_verified=False,
        points=0,
        streak_days=0,
        co2_saved_total=0,
    )
    db.add(user)
    db.flush()

    base_challenges = db.scalars(select(Challenge)).all()
    assign_challenges_for_user(db, user, base_challenges)
    db.add(ChatMessage(user_id=user.id, role="assistant", text="Привет. Я могу подсказать идеи на день, помочь с экопривычками или просто нормально ответить на вопрос."))
    db.commit()
    db.refresh(user)

    token = create_session_token(db, user)
    return AuthResponse(token=token, user=serialize_user(user))


@router.post("/admin/login", response_model=AdminSessionResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)) -> AdminSessionResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower().strip()))
    if not user or not verify_password(payload.password, user.password_hash) or user.role not in {"ADMIN", "MODERATOR"}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if needs_password_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
    token = create_session_token(db, user)
    return AdminSessionResponse(token=token, user=serialize_admin_identity(user))


@router.get("/admin/me", response_model=AdminIdentityResponse)
def admin_me(current_admin: User = Depends(get_current_admin)) -> AdminIdentityResponse:
    return serialize_admin_identity(current_admin)


@router.get("/bootstrap", response_model=BootstrapResponse)
def bootstrap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BootstrapResponse:
    user = fetch_user_with_relations(db, current_user.id)
    recalculate_user_progress(user)
    db.commit()
    user = fetch_user_with_relations(db, current_user.id)
    return build_bootstrap(user, db)


@router.get("/profile")
def profile(current_user: User = Depends(get_current_user)) -> dict[str, UserProfileResponse]:
    return {"user": serialize_user(current_user)}


@router.get("/activities")
def activities(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, list]:
    user = fetch_user_with_relations(db, current_user.id)
    return {"activities": [serialize_activity(item) for item in sorted(user.activities, key=lambda value: value.created_at, reverse=True)]}


@router.get("/challenges")
def challenges(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, list]:
    user = fetch_user_with_relations(db, current_user.id)
    return {"challenges": [serialize_user_challenge(item) for item in user.user_challenges]}


@router.get("/posts", response_model=PostsEnvelope)
def posts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PostsEnvelope:
    user = fetch_user_with_relations(db, current_user.id)
    return PostsEnvelope(posts=[serialize_post(item, viewer_id=user.id) for item in visible_posts_for_user(db, user)])


@router.get("/chat/messages", response_model=ChatEnvelope)
def chat_messages(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ChatEnvelope:
    user = fetch_user_with_relations(db, current_user.id)
    return ChatEnvelope(messages=[serialize_chat_message(item) for item in sorted(user.chat_messages, key=lambda value: value.created_at)])


@router.post("/activities", response_model=ActivityMutationResponse, status_code=status.HTTP_201_CREATED)
def add_activity(
    payload: ActivityCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityMutationResponse:
    now = datetime.now(timezone.utc)
    title = payload.title.strip()
    note = payload.note.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activity title is required.")

    user = fetch_user_with_relations(db, current_user.id)
    if not any(media.kind == "photo" for media in payload.media):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Добавь хотя бы одно фото для подтверждения активности.",
        )

    if payload.category == "Своя активность":
        computed_co2_saved, computed_points = estimate_custom_activity_impact(title, note)
    else:
        computed_points = max(0, min(payload.points, 60))
        computed_co2_saved = max(0.0, min(payload.co2Saved, 5.0))

    activity = Activity(
        user_id=user.id,
        category=payload.category,
        title=title,
        co2_saved=computed_co2_saved,
        points=computed_points,
        note=note or None,
        created_at=now,
    )
    db.add(activity)
    db.flush()
    for media in payload.media:
        db.add(
            ActivityMedia(
                activity_id=activity.id,
                kind=media.kind,
                data=base64.b64decode(media.base64Data.encode("utf-8")),
            )
        )
    db.refresh(user)
    user = fetch_user_with_relations(db, user.id)
    recalculate_user_progress(user)
    assign_challenges_for_user(db, user, db.scalars(select(Challenge)).all())
    db.flush()
    db.refresh(user)
    user = fetch_user_with_relations(db, user.id)
    recalculate_user_progress(user)

    if payload.shareToNews:
        post = Post(
            user_id=user.id,
            author_name=user.full_name or user.username,
            text=f"Добавил(а) активити: {title} ({payload.category})" + (f"\n{note}" if note else ""),
            moderation_state="Needs review",
            created_at=now,
        )
        db.add(post)
        db.flush()
        for media in payload.media:
            db.add(PostMedia(post_id=post.id, kind=media.kind, data=base64.b64decode(media.base64Data.encode("utf-8"))))

    db.commit()
    db.refresh(user)
    db.refresh(activity)
    user = fetch_user_with_relations(db, user.id)
    return ActivityMutationResponse(
        activity=serialize_activity(activity),
        user=serialize_user(user),
        challenges=[serialize_user_challenge(item) for item in user.user_challenges],
    )


@router.post("/posts", response_model=PostEnvelope, status_code=status.HTTP_201_CREATED)
def add_post(
    payload: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostEnvelope:
    if not payload.text.strip() and not payload.media:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post text or media is required.")
    user = fetch_user_with_relations(db, current_user.id)
    post = Post(
        user_id=current_user.id,
        author_name=current_user.full_name or current_user.username,
        text=payload.text.strip(),
        moderation_state="Needs review",
        created_at=datetime.now(timezone.utc),
    )
    db.add(post)
    db.flush()
    for media in payload.media:
        db.add(PostMedia(post_id=post.id, kind=media.kind, data=base64.b64decode(media.base64Data.encode("utf-8"))))
    db.flush()
    recalculate_user_progress(user)
    assign_challenges_for_user(db, user, db.scalars(select(Challenge)).all())
    db.flush()
    user = fetch_user_with_relations(db, current_user.id)
    recalculate_user_progress(user)
    db.commit()
    db.refresh(post)
    return PostEnvelope(post=serialize_post(post, viewer_id=current_user.id))


@router.post("/posts/{post_id}/report", status_code=status.HTTP_204_NO_CONTENT)
def report_post(
    post_id: str,
    payload: PostReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    reason = payload.reason.strip()
    if reason not in POST_REPORT_REASONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report reason.")

    post = db.scalar(select(Post).options(selectinload(Post.reports)).where(Post.id == parse_uuid(post_id)))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    if post.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot report your own post.")
    if post.moderation_state != "Published":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only published posts can be reported.")

    existing_report = next((item for item in post.reports if item.user_id == current_user.id), None)
    if existing_report:
        existing_report.reason = reason
    else:
        db.add(PostReport(post_id=post.id, user_id=current_user.id, reason=reason))
        db.flush()
        db.refresh(post)

    refreshed_post = db.scalar(select(Post).options(selectinload(Post.reports)).where(Post.id == post.id))
    refreshed_post.reports_count = len(refreshed_post.reports)
    db.commit()


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    post = db.scalar(
        select(Post)
        .options(
            selectinload(Post.user).selectinload(User.activities),
            selectinload(Post.user).selectinload(User.posts),
            selectinload(Post.user)
            .selectinload(User.user_challenges)
            .selectinload(UserChallenge.challenge),
        )
        .where(Post.id == parse_uuid(post_id))
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can delete only your own posts.")

    user_id = post.user.id
    db.delete(post)
    db.flush()
    db.expire_all()
    user = fetch_user_with_relations(db, user_id)
    recalculate_user_progress(user)
    assign_challenges_for_user(db, user, db.scalars(select(Challenge)).all())
    db.flush()
    db.expire_all()
    user = fetch_user_with_relations(db, user_id)
    recalculate_user_progress(user)
    db.commit()


@router.post("/chat/messages", response_model=ChatEnvelope, status_code=status.HTTP_201_CREATED)
def add_chat_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatEnvelope:
    trimmed_text = payload.text.strip()
    if not trimmed_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message text is required.")
    context_user = fetch_user_with_relations(db, current_user.id)
    user_message = ChatMessage(user_id=current_user.id, role="user", text=trimmed_text)
    assistant_message = ChatMessage(user_id=current_user.id, role="assistant", text=ai_response(trimmed_text, user=context_user))
    db.add_all([user_message, assistant_message])
    db.commit()
    db.refresh(user_message)
    db.refresh(assistant_message)
    return ChatEnvelope(messages=[serialize_chat_message(user_message), serialize_chat_message(assistant_message)])


@router.post("/challenges/{challenge_id}/claim", response_model=ChallengeClaimResponse)
def claim_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChallengeClaimResponse:
    user_challenge = db.scalar(
        select(UserChallenge)
        .options(selectinload(UserChallenge.challenge))
        .where(UserChallenge.user_id == current_user.id, UserChallenge.challenge_id == parse_uuid(challenge_id))
    )
    if not user_challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found.")
    if not user_challenge.is_completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Challenge is not completed yet.")
    if user_challenge.claimed_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Challenge reward already claimed.")

    user_challenge.claimed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_challenge)
    user = fetch_user_with_relations(db, current_user.id)
    refreshed = next(item for item in user.user_challenges if item.challenge_id == user_challenge.challenge_id)
    return ChallengeClaimResponse(
        user=serialize_user(user),
        challenge=serialize_user_challenge(refreshed),
        challenges=[serialize_user_challenge(item) for item in user.user_challenges],
    )


@router.get("/admin/users", response_model=list[AdminUserResponse])
def admin_users(
    role: str | None = None,
    status_value: str | None = Query(default=None, alias="status"),
    search: str | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserResponse]:
    stmt = select(User).options(selectinload(User.posts)).order_by(User.created_at.desc())
    if role:
        stmt = stmt.where(User.role == role)
    if status_value:
        stmt = stmt.where(User.status == status_value)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where((User.email.ilike(pattern)) | (User.username.ilike(pattern)))
    users = db.scalars(stmt).all()
    return [serialize_admin_user(user) for user in users]


@router.get("/admin/users/metrics", response_model=AdminUserMetrics)
def admin_user_metrics(_: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> AdminUserMetrics:
    users = db.scalars(select(User)).all()
    return AdminUserMetrics(
        totalUsers=len(users),
        adminCount=sum(1 for user in users if user.role in {"ADMIN", "MODERATOR"}),
        needsReview=sum(1 for user in users if user.status == "REVIEW"),
        verifiedCount=sum(1 for user in users if user.is_email_verified),
    )


@router.get("/admin/users/{user_id}", response_model=AdminUserDetailResponse)
def admin_user_detail(
    user_id: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserDetailResponse:
    user = db.scalar(
        select(User)
        .options(
            selectinload(User.activities).selectinload(Activity.media),
            selectinload(User.posts).selectinload(Post.media),
            selectinload(User.user_challenges).selectinload(UserChallenge.challenge),
        )
        .where(User.id == parse_uuid(user_id))
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return serialize_admin_user_detail(user)


@router.patch("/admin/users/{user_id}", response_model=AdminUserResponse)
def update_admin_user(
    user_id: str,
    payload: UpdateAdminUserRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    user = db.scalar(select(User).options(selectinload(User.posts)).where(User.id == parse_uuid(user_id)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current_admin.role == "MODERATOR":
        if user.role != "USER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Moderators can only manage regular users.",
            )
        if payload.role != user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Moderators cannot change user roles.",
            )
    user.role = payload.role
    user.status = payload.status
    user.admin_note = payload.adminNote.strip() or None
    db.commit()
    db.refresh(user)
    return serialize_admin_user(user)


@router.post("/admin/users/{user_id}/verify-email", response_model=AdminUserResponse)
def verify_admin_user_email(
    user_id: str,
    _: User = Depends(get_current_root_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    user = db.scalar(select(User).options(selectinload(User.posts)).where(User.id == parse_uuid(user_id)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_email_verified = True
    db.commit()
    db.refresh(user)
    return serialize_admin_user(user)


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_user(
    user_id: str,
    current_admin: User = Depends(get_current_root_admin),
    db: Session = Depends(get_db),
) -> None:
    user = db.scalar(select(User).where(User.id == parse_uuid(user_id)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account.",
        )
    db.delete(user)
    db.commit()


@router.get("/admin/activities", response_model=list[AdminUserActivityResponse])
def admin_activities(
    search: str | None = None,
    category: str | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserActivityResponse]:
    stmt = (
        select(Activity)
        .options(selectinload(Activity.user))
        .order_by(Activity.created_at.desc())
    )
    if category:
        stmt = stmt.where(Activity.category.ilike(category.strip()))
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.join(Activity.user).where(
            Activity.title.ilike(pattern)
            | Activity.category.ilike(pattern)
            | Activity.note.ilike(pattern)
            | User.username.ilike(pattern)
            | User.email.ilike(pattern)
        )
    activities = db.scalars(stmt).all()
    return [serialize_admin_activity(item) for item in activities]


@router.get("/admin/activities/metrics", response_model=AdminActivityMetrics)
def admin_activity_metrics(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminActivityMetrics:
    activities = db.scalars(select(Activity)).all()
    return AdminActivityMetrics(
        totalActivities=len(activities),
        totalPoints=sum(item.points for item in activities),
        totalCo2Saved=round(sum(item.co2_saved for item in activities), 2),
        uniqueUsers=len({item.user_id for item in activities}),
    )


@router.get("/admin/activities/{activity_id}", response_model=AdminActivityDetailResponse)
def admin_activity_detail(
    activity_id: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminActivityDetailResponse:
    activity = db.scalar(
        select(Activity)
        .options(selectinload(Activity.user), selectinload(Activity.media))
        .where(Activity.id == parse_uuid(activity_id))
    )
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found.")
    return serialize_admin_activity_detail(activity)


@router.get("/admin/dashboard/eco-analytics", response_model=EcoAnalyticsResponse)
def admin_eco_analytics(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> EcoAnalyticsResponse:
    fixed_categories = ["Транспорт", "Вода", "Пластик", "Отходы", "Энергия"]
    category_stats = {
        category: {"count": 0, "co2Saved": 0.0}
        for category in fixed_categories
    }
    top_users: dict[str, dict[str, str | int | float]] = {}
    custom_activities_count = 0

    activities = db.scalars(select(Activity).options(selectinload(Activity.user))).all()

    for activity in activities:
        if activity.category == "Своя активность":
            custom_activities_count += 1
        elif activity.category in category_stats:
            category_stats[activity.category]["count"] += 1
            category_stats[activity.category]["co2Saved"] += activity.co2_saved

        user_key = str(activity.user.id)
        if user_key not in top_users:
            top_users[user_key] = {
                "userId": user_key,
                "username": activity.user.username,
                "activitiesCount": 0,
                "ecoPoints": activity.user.points,
                "co2Saved": activity.user.co2_saved_total,
            }
        top_users[user_key]["activitiesCount"] += 1

    ordered_breakdown = [
        EcoAnalyticsCategoryResponse(
            category=category,
            count=category_stats[category]["count"],
            co2Saved=round(category_stats[category]["co2Saved"], 2),
        )
        for category in fixed_categories
    ]

    top_category = max(
        ordered_breakdown,
        key=lambda item: (item.count, item.co2Saved, -fixed_categories.index(item.category)),
    ).category if ordered_breakdown else ""

    average_co2 = round(
        sum(activity.co2_saved for activity in activities) / len(activities),
        2,
    ) if activities else 0.0

    top_users_by_activity = sorted(
        (
            EcoAnalyticsTopUserResponse(
                userId=item["userId"],
                username=item["username"],
                activitiesCount=item["activitiesCount"],
                ecoPoints=item["ecoPoints"],
                co2Saved=item["co2Saved"],
            )
            for item in top_users.values()
        ),
        key=lambda item: (-item.activitiesCount, -item.co2Saved, item.username.lower()),
    )[:5]

    return EcoAnalyticsResponse(
        categoryBreakdown=ordered_breakdown,
        topCategory=top_category,
        customActivitiesCount=custom_activities_count,
        averageCo2PerActivity=average_co2,
        topUsersByActivity=top_users_by_activity,
    )


@router.delete("/admin/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_activity(
    activity_id: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    activity = db.scalar(
        select(Activity)
        .options(
            selectinload(Activity.user).selectinload(User.activities),
            selectinload(Activity.user).selectinload(User.posts),
            selectinload(Activity.user)
            .selectinload(User.user_challenges)
            .selectinload(UserChallenge.challenge),
        )
        .where(Activity.id == parse_uuid(activity_id))
    )
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found.")
    user_id = activity.user.id
    db.delete(activity)
    db.flush()
    db.expire_all()
    user = fetch_user_with_relations(db, user_id)
    recalculate_user_progress(user)
    assign_challenges_for_user(db, user, db.scalars(select(Challenge)).all())
    db.flush()
    db.expire_all()
    user = fetch_user_with_relations(db, user_id)
    recalculate_user_progress(user)
    db.commit()


@router.get("/admin/categories", response_model=list[EcoCategoryResponse])
def admin_categories(
    search: str | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[EcoCategoryResponse]:
    stmt = select(EcoCategory).order_by(EcoCategory.name.asc())
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            (EcoCategory.name.ilike(pattern))
            | (EcoCategory.description.ilike(pattern))
            | (EcoCategory.icon.ilike(pattern))
        )
    return [serialize_category(item) for item in db.scalars(stmt).all()]


@router.get("/admin/categories/metrics", response_model=CategoryMetricsResponse)
def admin_category_metrics(_: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> CategoryMetricsResponse:
    categories = db.scalars(select(EcoCategory)).all()
    return CategoryMetricsResponse(
        totalCategories=len(categories),
        uniqueColors=len({item.color for item in categories}),
        iconCount=len({item.icon for item in categories}),
    )


@router.patch("/admin/categories/{category_id}", response_model=EcoCategoryResponse)
def update_category(
    category_id: str,
    payload: UpdateCategoryRequest,
    _: User = Depends(get_current_root_admin),
    db: Session = Depends(get_db),
) -> EcoCategoryResponse:
    category = db.scalar(select(EcoCategory).where(EcoCategory.id == parse_uuid(category_id)))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    category.name = payload.name.strip()
    category.description = payload.description.strip()
    category.color = payload.color.strip()
    category.icon = payload.icon.strip()
    db.commit()
    db.refresh(category)
    return serialize_category(category)


@router.post("/admin/categories", response_model=EcoCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CreateCategoryRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> EcoCategoryResponse:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="System categories are fixed and cannot be added from admin.",
    )


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="System categories are fixed and cannot be deleted from admin.",
    )


@router.get("/admin/habits", response_model=list[HabitResponse])
def admin_habits(
    search: str | None = None,
    category: str | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[HabitResponse]:
    stmt = select(Habit).options(selectinload(Habit.category)).order_by(Habit.title.asc())
    if search or category:
        stmt = stmt.join(Habit.category)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where((Habit.title.ilike(pattern)) | (EcoCategory.name.ilike(pattern)))
    if category:
        stmt = stmt.where(EcoCategory.name == category)
    habits = db.scalars(stmt).all()
    return [serialize_habit(item) for item in habits]


@router.get("/admin/habits/metrics", response_model=HabitMetricsResponse)
def admin_habit_metrics(_: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> HabitMetricsResponse:
    habits = db.scalars(select(Habit).options(selectinload(Habit.category))).all()
    return HabitMetricsResponse(
        totalHabits=len(habits),
        totalPoints=sum(item.points for item in habits),
        categoriesUsed=len({item.category.name for item in habits}),
    )


@router.patch("/admin/habits/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: str,
    payload: UpdateHabitRequest,
    _: User = Depends(get_current_root_admin),
    db: Session = Depends(get_db),
) -> HabitResponse:
    habit = db.scalar(select(Habit).options(selectinload(Habit.category)).where(Habit.id == parse_uuid(habit_id)))
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found.")
    category = db.scalar(select(EcoCategory).where(EcoCategory.name == payload.category.strip()))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System category not found.",
        )
    habit.title = payload.title.strip()
    habit.points = payload.points
    habit.co2_value = payload.co2Value
    habit.water_value = payload.waterValue
    habit.energy_value = payload.energyValue
    habit.category_id = category.id
    db.commit()
    db.refresh(habit)
    return serialize_habit(db.scalar(select(Habit).options(selectinload(Habit.category)).where(Habit.id == parse_uuid(habit_id))))


@router.post("/admin/habits", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    payload: CreateHabitRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> HabitResponse:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="System activities are fixed and cannot be added from admin.",
    )


@router.delete("/admin/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="System activities are fixed and cannot be deleted from admin.",
    )


@router.get("/admin/achievements", response_model=list[AchievementResponse])
def admin_achievements(
    search: str | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AchievementResponse]:
    stmt = select(Challenge).order_by(Challenge.title.asc())
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where((Challenge.title.ilike(pattern)) | (Challenge.description.ilike(pattern)) | (Challenge.badge_symbol.ilike(pattern)))
    return [serialize_achievement(item) for item in db.scalars(stmt).all()]


@router.get("/admin/achievements/metrics", response_model=AchievementMetricsResponse)
def admin_achievement_metrics(_: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> AchievementMetricsResponse:
    achievements = db.scalars(select(Challenge)).all()
    return AchievementMetricsResponse(
        totalAchievements=len(achievements),
        totalRewardPoints=sum(item.reward_points for item in achievements),
        maxTargetValue=max((item.target_count for item in achievements), default=0),
    )


@router.patch("/admin/achievements/{achievement_id}", response_model=AchievementResponse)
def update_achievement(
    achievement_id: str,
    payload: UpdateAchievementRequest,
    _: User = Depends(get_current_root_admin),
    db: Session = Depends(get_db),
) -> AchievementResponse:
    challenge = db.scalar(select(Challenge).where(Challenge.id == parse_uuid(achievement_id)))
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Achievement not found.")
    challenge.title = payload.title.strip()
    challenge.description = payload.description.strip()
    challenge.badge_symbol = payload.icon.strip()
    challenge.target_count = payload.targetValue
    challenge.reward_points = payload.rewardPoints
    db.commit()
    db.refresh(challenge)
    return serialize_achievement(challenge)


@router.post("/admin/achievements", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
def create_achievement(
    payload: CreateAchievementRequest,
    _: User = Depends(get_current_root_admin),
    db: Session = Depends(get_db),
) -> AchievementResponse:
    if db.scalar(select(Challenge).where(Challenge.title == payload.title.strip())):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Achievement already exists.")
    challenge = Challenge(
        title=payload.title.strip(),
        description=payload.description.strip(),
        target_count=payload.targetValue,
        reward_points=payload.rewardPoints,
        badge_symbol=payload.icon.strip(),
        badge_tint_hex=payload.badgeTintHex,
        badge_background_hex=payload.badgeBackgroundHex,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return serialize_achievement(challenge)


@router.delete("/admin/achievements/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_achievement(
    achievement_id: str,
    _: User = Depends(get_current_root_admin),
    db: Session = Depends(get_db),
) -> None:
    challenge = db.scalar(select(Challenge).where(Challenge.id == parse_uuid(achievement_id)))
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Achievement not found.")
    db.delete(challenge)
    db.commit()


@router.get("/admin/posts", response_model=list[CommunityPostResponse])
def admin_posts(
    search: str | None = None,
    state: str | None = None,
    reports: str | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[CommunityPostResponse]:
    stmt = select(Post).order_by(Post.created_at.desc())
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where((Post.author_name.ilike(pattern)) | (Post.text.ilike(pattern)))
    if state:
        stmt = stmt.where(Post.moderation_state == state)
    if reports == "REPORTED":
        stmt = stmt.where(Post.reports_count > 0)
    elif reports == "NO_REPORTS":
        stmt = stmt.where(Post.reports_count == 0)
    return [serialize_admin_post(item) for item in db.scalars(stmt).all()]


@router.get("/admin/posts/metrics", response_model=PostMetricsResponse)
def admin_post_metrics(_: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> PostMetricsResponse:
    posts = db.scalars(select(Post)).all()
    return PostMetricsResponse(
        totalPosts=len(posts),
        needsReviewPosts=sum(1 for item in posts if item.moderation_state == "Needs review"),
        hiddenPosts=sum(1 for item in posts if item.moderation_state == "Hidden"),
        totalReports=sum(item.reports_count for item in posts),
    )


@router.get("/admin/posts/{post_id}", response_model=CommunityPostDetailResponse)
def admin_post_detail(
    post_id: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> CommunityPostDetailResponse:
    post = db.scalar(select(Post).options(selectinload(Post.media), selectinload(Post.reports)).where(Post.id == parse_uuid(post_id)))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return serialize_admin_post_detail(post)


@router.patch("/admin/posts/{post_id}", response_model=CommunityPostResponse)
def update_admin_post(
    post_id: str,
    payload: UpdatePostRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> CommunityPostResponse:
    post = db.scalar(select(Post).where(Post.id == parse_uuid(post_id)))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    post.moderation_state = payload.state
    cleaned_note = payload.moderatorNote.strip()
    if payload.state == "Hidden":
        post.moderator_note = cleaned_note or "Нарушает правила сообщества"
    elif payload.state == "Published":
        post.moderator_note = cleaned_note or None
    else:
        post.moderator_note = cleaned_note or None
    db.commit()
    db.refresh(post)
    return serialize_admin_post(post)


@router.post("/admin/posts", response_model=CommunityPostResponse, status_code=status.HTTP_201_CREATED)
def create_admin_post(
    payload: CreateAdminPostRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> CommunityPostResponse:
    author = payload.author.strip()
    content = payload.content.strip()
    if not author or not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author and content are required.")
    post = Post(
        user_id=current_admin.id,
        author_name=author,
        text=content,
        visibility="PUBLIC",
        moderation_state=payload.state,
        reports_count=payload.reportsCount,
        created_at=datetime.now(timezone.utc),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return serialize_admin_post(post)


@router.delete("/admin/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    post = db.scalar(
        select(Post)
        .options(
            selectinload(Post.user).selectinload(User.activities),
            selectinload(Post.user).selectinload(User.posts),
            selectinload(Post.user)
            .selectinload(User.user_challenges)
            .selectinload(UserChallenge.challenge),
        )
        .where(Post.id == parse_uuid(post_id))
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    user_id = post.user.id
    db.add(
        ChatMessage(
            user_id=user_id,
            role="assistant",
            text="Публикация не прошла модерацию. Нарушает правила сообщества.",
        )
    )
    db.delete(post)
    db.flush()
    db.expire_all()
    user = fetch_user_with_relations(db, user_id)
    recalculate_user_progress(user)
    assign_challenges_for_user(db, user, db.scalars(select(Challenge)).all())
    db.flush()
    db.expire_all()
    user = fetch_user_with_relations(db, user_id)
    recalculate_user_progress(user)
    db.commit()
