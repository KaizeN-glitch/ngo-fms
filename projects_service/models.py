from sqlalchemy import Column, String
from database import Base

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False) 