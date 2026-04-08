from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    video_prima: str
    video_dopo: str
