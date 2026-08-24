from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

import os
import tempfile

from models import CaseStudyIntake, WorkflowStatusUpdate

from services import (
    advance_to_fathom_search,
    add_quote_pdf_to_workflow,
    create_workflow,
    generate_case_study_for_workflow,
    get_workflow,
    process_case_study_workflow,
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


# PATCH endpoint used to start the Fathom meeting search.
@router.patch("/v1/case-studies/{workflow_id}/start-fathom-search")
def start_fathom_search(workflow_id: str):

    # Send the workflow ID to services.py to begin the Fathom search.
    workflow = advance_to_fathom_search(workflow_id)

    # Return 404 Not Found if the workflow does not exist.
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Return the updated workflow.
    return workflow


# POST endpoint used to upload a quote PDF to an existing workflow.
@router.post("/v1/case-studies/{workflow_id}/quote-pdf")
async def upload_quote_pdf(
    workflow_id: str,
    file: UploadFile = File(...),
):

    # Make sure the uploaded file is a PDF.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )

    # Find the existing workflow.
    workflow = get_workflow(workflow_id)

    # Return 404 Not Found if the workflow does not exist.
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Temporarily save the uploaded PDF.
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp_file:
        file_bytes = await file.read()
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

    try:
        # Extract the PDF text and add it to the workflow.
        updated_workflow = add_quote_pdf_to_workflow(
            workflow_id,
            temp_file_path,
        )

    finally:
        # Delete the temporary PDF after it has been processed.
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Return the updated workflow.
    return updated_workflow


# Generate the case study draft using the collected workflow sources.
@router.patch("/v1/case-studies/{workflow_id}/generate-draft")
def generate_case_study_draft(workflow_id: str):

    # Make sure the workflow exists.
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Generate the case study draft.
    updated_workflow = generate_case_study_for_workflow(workflow_id)

    # Both the quote PDF and Fathom transcripts are required.
    if updated_workflow is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quote PDF and Fathom transcripts are required before generating the draft.",
        )

    return {
    "workflow_id": updated_workflow["workflow_id"],
    "stage": updated_workflow["stage"],
    "client_name": updated_workflow["client_name"],
    "project_name": updated_workflow["project_name"],
    "emanage_job_number": updated_workflow["emanage_job_number"],
    "case_study_draft": updated_workflow["case_study_draft"],
    "case_study_document_path": updated_workflow["case_study_document_path"],
}


# Run the full case study workflow using the uploaded quote PDF.
@router.post("/v1/case-studies/{workflow_id}/process")
def process_case_study(
    workflow_id: str,
    file: UploadFile = File(...),
):

    # Make sure the uploaded file is a PDF.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )

    # Make sure the workflow exists.
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Temporarily save the uploaded PDF.
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp_file:

        temp_file.write(file.file.read())
        temp_file_path = temp_file.name

    try:
        # Run the complete workflow automatically.
        completed_workflow = process_case_study_workflow(
            workflow_id,
            temp_file_path,
        )

        if completed_workflow is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case study workflow could not be completed.",
            )

        return completed_workflow

    finally:
        # Delete the temporary PDF after processing.
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# Create and process a complete case study workflow from one request.
@router.post("/v1/case-studies/intake-and-process")
def intake_and_process_case_study(
    client_name: str = Form(...),
    project_name: str = Form(...),
    emanage_job_number: str | None = Form(None),
    message_id: str = Form(...),
    sender_email: str = Form(...),
    email_subject: str = Form(...),
    file: UploadFile = File(...),
):

    # Make sure the uploaded file is a PDF.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )

    # Build the case study intake information.
    intake = CaseStudyIntake(
        client_name=client_name,
        project_name=project_name,
        emanage_job_number=emanage_job_number,
        message_id=message_id,
        sender_email=sender_email,
        email_subject=email_subject,
    )

    # Create the workflow.
    workflow = create_workflow(intake)

    # Return 403 Forbidden if the sender is not approved.
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sender is not approved.",
        )

    workflow_id = workflow["workflow_id"]

    # Temporarily save the uploaded quote PDF.
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp_file:

        temp_file.write(file.file.read())
        temp_file_path = temp_file.name

    try:
        # Run the entire case study workflow automatically.
        completed_workflow = process_case_study_workflow(
            workflow_id,
            temp_file_path,
        )

        if completed_workflow is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case study workflow could not be completed.",
            )

        return completed_workflow

    finally:
        # Delete the temporary PDF after processing.
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)