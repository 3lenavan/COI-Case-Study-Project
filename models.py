from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator


# Defines the overall status of a case study workflow.
class WorkflowStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"


# Defines the different stages a workflow can move through.
class WorkflowStage(str, Enum):
    INTAKE_RECEIVED = "INTAKE_RECEIVED"
    VALIDATING_REQUEST = "VALIDATING_REQUEST"
    SEARCHING_CLIENT = "SEARCHING_CLIENT"
    SEARCHING_FATHOM = "SEARCHING_FATHOM"
    GENERATING_DRAFT = "GENERATING_DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    COMPLETED = "COMPLETED"


# Defines the data required when updating a workflow's status.
class WorkflowStatusUpdate(BaseModel):
    status: WorkflowStatus


# Defines and validates the information received when a new case study workflow is created.
class CaseStudyIntake(BaseModel):
    client_name: str | None = None
    project_name: str | None = None
    emanage_job_number: str | None = None
    message_id: str
    sender_email: EmailStr
    email_subject: str
    email_body: str | None = None

    # Run the validator on each of these required fields.
    @field_validator(
        "message_id",
        "sender_email",
        "email_subject",
    )
    @classmethod
    def fields_cannot_be_blank(cls, value: str) -> str:

        # Remove extra spaces from the beginning and end of the value.
        cleaned_value = value.strip()

        # Reject the request if the field only contains blank spaces.
        if not cleaned_value:
            raise ValueError("Field cannot be blank")

        # Return the cleaned value after it passes validation.
        return cleaned_value