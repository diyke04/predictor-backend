

from pydantic import BaseModel


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str