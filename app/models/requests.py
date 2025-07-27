from pydantic import BaseModel, Field
from typing import Optional
from fastapi import UploadFile


class ConvertRequest(BaseModel):
    """Request model for markdown to PDF conversion."""
    title: str = Field(default="Document", description="Document title for cover page")
    include_toc: bool = Field(default=True, description="Include table of contents")
    page_format: str = Field(default="A4", description="Page format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Project Proposal",
                "include_toc": True,
                "page_format": "A4"
            }
        }