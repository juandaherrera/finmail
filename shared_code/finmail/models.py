from pydantic import BaseModel


class EmailPayload(BaseModel):
    subject: str
    sender: str
    html: str | None = None
    text: str | None = None
