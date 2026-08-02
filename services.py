from datetime import datetime, timezone
from uuid import uuid4

from models import CaseStudyIntake


def create_workflow(intake: CaseStudyIntake) -> dict:
    workflow_id = str(uuid4())
    received_at = datetime.now(timezone.utc).isoformat()

    workflow = {
        "workflow_id": workflow_id,
        "status": "RECEIVED",
        "received_at": received_at,
        "source": "FastAPI Docs",
        "client_name": intake.client_name,
        "project_name": intake.project_name,
        "emanage_job_number": intake.emanage_job_number,
    }

    return workflow