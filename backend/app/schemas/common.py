from datetime import datetime

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: str


class ChatRequest(BaseModel):
    text: str


class MediaPayload(APIModel):
    id: str
    kind: str
    base64Data: str


class ChatMessageResponse(APIModel):
    id: str
    isUser: bool
    text: str
    createdAt: datetime
