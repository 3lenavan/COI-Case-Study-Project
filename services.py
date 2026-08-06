from datetime import datetime, timezone
from uuid import uuid4

from config import APPROVED_SENDERS
from models import CaseStudyIntake, WorkflowStage, WorkflowStatus
from storage import workflows


def get_workflow_by_message_id(message_id: str) -> dict | None:
    for workflow in workflows.values():
        if workflow["message_id"] == message_id:
            return workflow

    return None


def is_approved_sender(sender_email: str) -> bool:
    return sender_email.lower() in APPROVED_SENDERS


def create_workflow(intake: CaseStudyIntake) -> dict | None:
    if not is_approved_sender(str(intake.sender_email)):
        return None

    existing_workflow = get_workflow_by_message_id(intake.message_id)

    if existing_workflow is not None:
        return existing_workflow

    workflow_id = str(uuid4())
    current_time = datetime.now(timezone.utc).isoformat()

    workflow = {
        "workflow_id": workflow_id,
        "status": WorkflowStatus.RECEIVED,
        "stage": WorkflowStage.INTAKE_RECEIVED,
        "received_at": current_time,
        "updated_at": current_time,
        "source": "FastAPI Docs",
        "client_name": intake.client_name,
        "project_name": intake.project_name,
        "emanage_job_number": intake.emanage_job_number,
        "message_id": intake.message_id,
        "sender_email": intake.sender_email,
        "email_subject": intake.email_subject,
    }

    workflows[workflow_id] = workflow

    return workflow


def get_workflow(workflow_id: str) -> dict | None:
    return workflows.get(workflow_id)


def update_workflow_status(
    workflow_id: str,
    new_status: WorkflowStatus,
) -> dict | None:
    workflow = workflows.get(workflow_id)

    if workflow is None:
        return None

    workflow["status"] = new_status

    if new_status == WorkflowStatus.VALIDATED:
        workflow["stage"] = WorkflowStage.SEARCHING_CLIENT

    workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

    return workflow

def advance_to_fathom_search(workflow_id: str) -> dict | None:
    workflow = workflows.get(workflow_id)

    if workflow is None:
        return None

    workflow["stage"] = WorkflowStage.SEARCHING_FATHOM
    workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

    return workflow