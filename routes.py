from fastapi import APIRouter, HTTPException, status

from models import CaseStudyIntake, WorkflowStatusUpdate
from services import (
    advance_to_fathom_search,
    create_workflow,
    get_workflow,
    update_workflow_status,
)

router = APIRouter()


@router.post(
    "/v1/case-studies/intake",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_case_study_intake(intake: CaseStudyIntake):
    workflow = create_workflow(intake)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sender is not approved",
        )

    return workflow


@router.get("/v1/case-studies/{workflow_id}")
def read_workflow(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    return workflow


@router.patch("/v1/case-studies/{workflow_id}/status")
def change_workflow_status(
    workflow_id: str,
    status_update: WorkflowStatusUpdate,
):
    workflow = update_workflow_status(
        workflow_id,
        status_update.status,
    )

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    return workflow

@router.patch("/v1/case-studies/{workflow_id}/start-fathom-search")
def start_fathom_search(workflow_id: str):
    workflow = advance_to_fathom_search(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    return workflow