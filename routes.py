from fastapi import APIRouter, HTTPException, status

from models import CaseStudyIntake, WorkflowStatusUpdate
from services import (
    advance_to_fathom_search,
    create_workflow,
    get_workflow,
    update_workflow_status,
)


# Creates a router that holds the case study API endpoints.
router = APIRouter()


# POST endpoint used to create a new case study workflow.
@router.post(
    "/v1/case-studies/intake",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_case_study_intake(intake: CaseStudyIntake):

    # Send the intake information to services.py to create the workflow.
    workflow = create_workflow(intake)

    # Return 403 Forbidden if the sender is not approved.
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sender is not approved",
        )

    # Return the created workflow.
    return workflow


# GET endpoint used to retrieve an existing workflow by its workflow ID.
@router.get("/v1/case-studies/{workflow_id}")
def read_workflow(workflow_id: str):

    # Search for the workflow using its ID.
    workflow = get_workflow(workflow_id)

    # Return 404 Not Found if the workflow does not exist.
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Return the workflow if it was found.
    return workflow


# PATCH endpoint used to change the status of an existing workflow.
@router.patch("/v1/case-studies/{workflow_id}/status")
def change_workflow_status(
    workflow_id: str,
    status_update: WorkflowStatusUpdate,
):

    # Send the workflow ID and new status to services.py.
    workflow = update_workflow_status(
        workflow_id,
        status_update.status,
    )

    # Return 404 Not Found if the workflow does not exist.
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Return the updated workflow.
    return workflow


# PATCH endpoint used to move a workflow to the Fathom search stage.
@router.patch("/v1/case-studies/{workflow_id}/start-fathom-search")
def start_fathom_search(workflow_id: str):

    # Tell services.py to move the workflow to SEARCHING_FATHOM.
    workflow = advance_to_fathom_search(workflow_id)

    # Return 404 Not Found if the workflow does not exist.
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Return the workflow with its updated stage.
    return workflow