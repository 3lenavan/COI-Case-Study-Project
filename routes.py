from fastapi import APIRouter, HTTPException, status

from models import CaseStudyIntake
from services import create_workflow, get_workflow

router = APIRouter()


@router.post(
    "/v1/case-studies/intake",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_case_study_intake(intake: CaseStudyIntake):
    return create_workflow(intake)

@router.get("/v1/case-studies/{workflow_id}")
def read_workflow(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    return workflow