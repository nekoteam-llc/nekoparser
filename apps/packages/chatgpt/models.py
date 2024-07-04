from pydantic import BaseModel


class ChatGPTQuery(BaseModel):
    user_message: str
    system_message: str
