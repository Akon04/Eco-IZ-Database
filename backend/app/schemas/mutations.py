from datetime import datetime

from pydantic import BaseModel

from app.schemas.bootstrap import ActivityResponse, ChallengeResponse, ChatMessageResponse, PostMediaResponse, PostResponse, UserProfileResponse


class ActivityCreateRequest(BaseModel):
    category: str
    title: str
    co2Saved: float
    points: int
    note: str = ""
    media: list[PostMediaResponse] = []
    shareToNews: bool = True


class ActivityMutationResponse(BaseModel):
    activity: ActivityResponse
    user: UserProfileResponse
    challenges: list[ChallengeResponse]


class EcoEventResponse(BaseModel):
    id: str
    title: str
    description: str
    location: str
    startsAt: datetime
    rewardPoints: int
    badge: str
    partnerName: str | None = None
    registrationUrl: str | None = None
    imageTintHex: int


class EcoEventsEnvelope(BaseModel):
    events: list[EcoEventResponse]


class PostCreateRequest(BaseModel):
    text: str = ""
    media: list[PostMediaResponse] = []


class PostReportRequest(BaseModel):
    reason: str


class PostEnvelope(BaseModel):
    post: PostResponse


class PostsEnvelope(BaseModel):
    posts: list[PostResponse]


class ChatEnvelope(BaseModel):
    messages: list[ChatMessageResponse]


class ChallengeClaimResponse(BaseModel):
    user: UserProfileResponse
    challenge: ChallengeResponse
    challenges: list[ChallengeResponse]
