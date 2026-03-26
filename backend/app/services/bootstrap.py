import base64

from app.models.chat import ChatMessage
from app.models.challenge import Challenge
from app.models.challenge import UserChallenge
from app.models.post import Post, PostMedia
from app.models.user import Activity, User
from app.schemas.bootstrap import (
    ActivityResponse,
    BootstrapResponse,
    ChallengeResponse,
    ChatMessageResponse,
    PostMediaResponse,
    PostResponse,
    UserProfileResponse,
)


def user_level_number(points: int) -> int:
    if points < 120:
        return 1
    if points < 320:
        return 2
    return 3


def user_level(points: int) -> str:
    level_number = user_level_number(points)
    if level_number == 1:
        return "Эко-новичок"
    if level_number == 2:
        return "Эко-воин"
    return "Хранитель Земли"


def unlocked_challenge_count(points: int) -> int:
    return user_level_number(points) * 5


def challenge_sort_key(challenge: Challenge) -> tuple[int, str]:
    return (challenge.reward_points, challenge.title)


def serialize_user(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        id=str(user.id),
        fullName=user.full_name,
        email=user.email,
        points=user.points,
        streakDays=user.streak_days,
        co2SavedTotal=user.co2_saved_total,
        level=user_level(user.points),
    )


def serialize_activity(activity: Activity) -> ActivityResponse:
    return ActivityResponse(
        id=str(activity.id),
        category=activity.category,
        title=activity.title,
        co2Saved=activity.co2_saved,
        points=activity.points,
        createdAt=activity.created_at,
    )


def serialize_user_challenge(item: UserChallenge) -> ChallengeResponse:
    challenge = item.challenge
    return ChallengeResponse(
        id=str(challenge.id),
        title=challenge.title,
        description=challenge.description,
        targetCount=challenge.target_count,
        currentCount=item.current_count,
        rewardPoints=challenge.reward_points,
        badgeSymbol=challenge.badge_symbol,
        badgeTintHex=challenge.badge_tint_hex,
        badgeBackgroundHex=challenge.badge_background_hex,
        isCompleted=item.is_completed,
        isClaimed=item.claimed_at is not None,
    )


def serialize_media(item: PostMedia) -> PostMediaResponse:
    return PostMediaResponse(
        id=str(item.id),
        kind=item.kind,
        base64Data=base64.b64encode(item.data).decode("utf-8"),
    )


def serialize_post(post: Post) -> PostResponse:
    return PostResponse(
        id=str(post.id),
        author=post.author_name,
        text=post.text,
        createdAt=post.created_at,
        media=[serialize_media(media) for media in post.media],
    )


def serialize_chat_message(message: ChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=str(message.id),
        isUser=message.role == "user",
        text=message.text,
        createdAt=message.created_at,
    )


def build_bootstrap(user: User) -> BootstrapResponse:
    return BootstrapResponse(
        user=serialize_user(user),
        activities=[serialize_activity(item) for item in sorted(user.activities, key=lambda value: value.created_at, reverse=True)],
        challenges=[serialize_user_challenge(item) for item in user.user_challenges],
        posts=[serialize_post(item) for item in sorted(user.posts, key=lambda value: value.created_at, reverse=True)],
        chatMessages=[serialize_chat_message(item) for item in sorted(user.chat_messages, key=lambda value: value.created_at)],
    )
