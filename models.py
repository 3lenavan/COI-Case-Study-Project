from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator


class WorkflowStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"


class WorkflowStage(str, Enum):
    INTAKE_RECEIVED = "INTAKE_RECEIVED"
    VALIDATING_REQUEST = "VALIDATING_REQUEST"
    SEARCHING_CLIENT = "SEARCHING_CLIENT"
    SEARCHING_FATHOM = "SEARCHING_FATHOM"
    GENERATING_DRAFT = "GENERATING_DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    COMPLETED = "COMPLETED"


class WorkflowStatusUpdate(BaseModel):
    status: WorkflowStatus


class CaseStudyIntake(BaseModel):
    client_name: str
    project_name: str
    emanage_job_number: str | None = None
    message_id: str
    sender_email: EmailStr
    email_subject: str

    @field_validator(
        "client_name",
        "project_name",
        "message_id",
        "sender_email",
        "email_subject",
    )
    @classmethod
    def fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Field cannot be blank")

        return cleaned_value