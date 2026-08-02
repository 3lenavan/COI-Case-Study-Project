from uuid import uuid4

from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class CaseStudyIntake(BaseModel):
    client_name: str
    project_name: str
    emanage_job_number: str | None = None


@app.get("/")
def read_root():
    return {"message": "COI Case Study Automation API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/v1/case-studies/intake", status_code=status.HTTP_202_ACCEPTED)
def create_case_study_intake(intake: CaseStudyIntake):
    workflow_id = str(uuid4())

    return {
        "workflow_id": workflow_id,
        "status": "RECEIVED",
        "client_name": intake.client_name,
        "project_name": intake.project_name,
        "emanage_job_number": intake.emanage_job_number,
    }