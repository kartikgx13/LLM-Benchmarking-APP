from pydantic import BaseModel


class ModelStatus(BaseModel):
    name: str
    installed: bool