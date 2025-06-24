from pydantic import BaseModel

class ProjectCreate(BaseModel):
    project_id: str
    name: str

class ProjectOut(BaseModel):
    project_id: str
    name: str

    class Config:
        from_attributes = True 