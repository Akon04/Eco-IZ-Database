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


class PostCreateRequest(BaseModel):
    text: str = ""
    media: list[PostMediaResponse] = []


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
