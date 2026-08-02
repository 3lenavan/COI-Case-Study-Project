from fastapi import APIRouter, status

from models import CaseStudyIntake
from services import create_workflow

router = APIRouter()


@router.post(
    "/v1/case-studies/intake",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_case_study_intake(intake: CaseStudyIntake):
    return create_workflow(intake)