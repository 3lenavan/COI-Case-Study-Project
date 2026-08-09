from fathom_service import find_meetings_by_client
from datetime import datetime, timezone
from uuid import uuid4

from config import APPROVED_SENDERS
from models import CaseStudyIntake, WorkflowStage, WorkflowStatus
from storage import workflows


# Search existing workflows for one with the same email message ID.
# This helps prevent the same email from creating duplicate workflows.
def get_workflow_by_message_id(message_id: str) -> dict | None:
    for workflow in workflows.values():
        if workflow["message_id"] == message_id:
            return workflow

    return None


# Check whether the email sender is allowed to create a case study workflow.
def is_approved_sender(sender_email: str) -> bool:
    return sender_email.lower() in APPROVED_SENDERS


# Create and store a new case study workflow.
def create_workflow(intake: CaseStudyIntake) -> dict | None:

    # Reject the request if the sender is not approved.
    if not is_approved_sender(str(intake.sender_email)):
        return None

    # Check whether this email has already created a workflow.
    existing_workflow = get_workflow_by_message_id(intake.message_id)

    # Return the existing workflow instead of creating a duplicate.
    if existing_workflow is not None:
        return existing_workflow

    # Generate a unique ID for this workflow.
    workflow_id = str(uuid4())

    # Record the current time in UTC.
    current_time = datetime.now(timezone.utc).isoformat()

    # Build the workflow using the information from the intake request.
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

    # Save the workflow in temporary storage.
    workflows[workflow_id] = workflow

    return workflow


# Find and return a workflow using its workflow ID.
def get_workflow(workflow_id: str) -> dict | None:
    return workflows.get(workflow_id)


# Update the status of an existing workflow.
def update_workflow_status(
    workflow_id: str,
    new_status: WorkflowStatus,
) -> dict | None:

    # Find the workflow in temporary storage.
    workflow = workflows.get(workflow_id)

    # Return None if the workflow does not exist.
    if workflow is None:
        return None

    # Update the workflow's status.
    workflow["status"] = new_status

    # Once validation succeeds, begin searching for the client.
    if new_status == WorkflowStatus.VALIDATED:
        workflow["stage"] = WorkflowStage.SEARCHING_CLIENT

    # Record when the workflow was last changed.
    workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

    return workflow


# Move the workflow to the Fathom meeting search stage.
def advance_to_fathom_search(workflow_id: str) -> dict | None:

    # Find the workflow in temporary storage.
    workflow = workflows.get(workflow_id)

    # Return None if the workflow does not exist.
    if workflow is None:
        return None

    # Update the stage to show that Fathom meetings are being searched.
    workflow["stage"] = WorkflowStage.SEARCHING_FATHOM

    # Search for meetings that contain the client name in their title.
    client_name = workflow["client_name"]

    # Use the Fathom service to find meetings that match the client name.
    matching_meetings = find_meetings_by_client(client_name)

    # Store the matching meetings in the workflow for later review.
    workflow["fathom_meetings"] = matching_meetings

    # Update the timestamp because the workflow changed.
    workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

    return workflow