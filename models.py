from enum import Enum

from pydantic import BaseModel, field_validator

class WorkflowStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"

class WorkflowStatusUpdate(BaseModel):
    status: WorkflowStatus

class CaseStudyIntake(BaseModel):
    client_name: str
    project_name: str
    emanage_job_number: str | None = None

    @field_validator("client_name", "project_name")
    @classmethod
    def fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Field cannot be blank")

        return cleaned_value