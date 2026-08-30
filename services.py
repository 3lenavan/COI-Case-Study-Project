from document_service import save_case_study_document

from pdf_service import extract_text_from_pdf

from ai_service import build_case_study_prompt, generate_case_study_draft

from fathom_service import (
    find_meetings_by_client,
    get_transcripts_for_meetings,
    format_transcripts_for_ai,
)

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


# Build a prompt for the AI to generate a case study draft.
def extract_email_details(email_body: str | None) -> dict:
    details = {
        "client_name": None,
        "project_name": None,
    }

    if not email_body:
        return details

    for line in email_body.splitlines():
        cleaned_line = line.strip()

        if cleaned_line.lower().startswith("client:"):
            details["client_name"] = cleaned_line.split(":", 1)[1].strip()

        elif cleaned_line.lower().startswith("project:"):
            details["project_name"] = cleaned_line.split(":", 1)[1].strip()

    return details

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

    # Extract client and project details from the email body.
    email_details = extract_email_details(intake.email_body)

    client_name = intake.client_name or email_details["client_name"]
    project_name = intake.project_name or email_details["project_name"]

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
        "client_name": client_name,
        "project_name": project_name,
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

    # Make sure the client name is available before searching Fathom.
    client_name = workflow.get("client_name")

    if not client_name:
        raise ValueError("Client name is required before starting Fathom search.")

    # Use the first word of the client name for a broader Fathom search.
    fathom_search_name = client_name.split()[0]

    # Test
    matching_meetings = find_meetings_by_client(fathom_search_name)

    print("\n========== LIVE FATHOM SEARCH ==========")
    print("Client being searched:", fathom_search_name)
    print("Number of meetings found:", len(matching_meetings))

    for meeting in matching_meetings:
            print(
                meeting["title"],
        "-",
        meeting["recording_id"],
    )

    # Retrieve transcripts for the matching client meetings.
    meetings_with_transcripts = get_transcripts_for_meetings(
        matching_meetings
    )

    # Format the Fathom transcripts into clean text for AI.
    formatted_transcripts = format_transcripts_for_ai(
        meetings_with_transcripts
    )

    # Store the formatted transcript text for future AI generation.
    workflow["formatted_fathom_transcripts"] = formatted_transcripts

    # Store the matching meetings in the workflow for later review.
    workflow["fathom_meetings"] = meetings_with_transcripts

    # Prepare the information that will be sent to the AI for case study generation.
    case_study_sources = build_case_study_sources(workflow_id)

    # Store the case study sources in the workflow for later use.
    workflow["case_study_sources"] = case_study_sources

    # Build the prompt that will eventually be sent to the AI.
    case_study_prompt = build_case_study_prompt(case_study_sources)

    # Store the AI prompt in the workflow.
    workflow["case_study_prompt"] = case_study_prompt

    # Move to the case study draft generation stage.
    workflow["stage"] = WorkflowStage.GENERATING_DRAFT

    # Update the timestamp because the workflow changed.
    workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

    return workflow


# Prepare the collected workflow information for case study generation.
def build_case_study_sources(workflow_id: str) -> dict | None:

    # Find the workflow in temporary storage.
    workflow = workflows.get(workflow_id)

    # Return None if the workflow does not exist.
    if workflow is None:
        return None

    # Gather the information that will eventually be sent to the AI.
    case_study_sources = {
        "client_name": workflow["client_name"],
        "project_name": workflow["project_name"],
        "emanage_job_number": workflow["emanage_job_number"],
        "fathom_transcripts": workflow.get("formatted_fathom_transcripts"),
        "quote_pdf_text": workflow.get("quote_pdf_text"),
    }

    return case_study_sources

def extract_quote_details(quote_pdf_text: str) -> dict:
    details = {
        "client_name": None,
        "project_name": None,
        "emanage_job_number": None,
    }

    for line in quote_pdf_text.splitlines():
        cleaned_line = line.strip()

        if cleaned_line.startswith("Client:"):
            details["client_name"] = cleaned_line.split("Client:", 1)[1].strip()

        elif cleaned_line.startswith("Project:"):
            details["project_name"] = cleaned_line.split("Project:", 1)[1].strip()

        elif cleaned_line.startswith("eManage Job Number:"):
            details["emanage_job_number"] = cleaned_line.split(
                "eManage Job Number:", 1
            )[1].strip()

    return details


# Extract quote PDF text and store it in the workflow.
def add_quote_pdf_to_workflow(
    workflow_id: str,
    file_path: str,
) -> dict | None:
    workflow = workflows.get(workflow_id)

    # Return None if the workflow does not exist.
    if workflow is None:
        return None

    # Extract text from the quote PDF.
    quote_pdf_text = extract_text_from_pdf(file_path)

    # Store the extracted PDF text in the workflow.
    workflow["quote_pdf_text"] = quote_pdf_text

    # Extract important project information from the quote.
    quote_details = extract_quote_details(quote_pdf_text)

    # Update the workflow using information found in the PDF.
    if quote_details["client_name"]:
        workflow["client_name"] = quote_details["client_name"]

    if quote_details["project_name"]:
        workflow["project_name"] = quote_details["project_name"]

    if quote_details["emanage_job_number"]:
        workflow["emanage_job_number"] = quote_details["emanage_job_number"]


    # Rebuild the case study sources with the new PDF information.
    workflow["case_study_sources"] = build_case_study_sources(workflow_id)

    # Build the prompt that will eventually be sent to the AI.
    case_study_prompt = build_case_study_prompt(
        workflow["case_study_sources"]
)
    # Store the AI prompt in the workflow.
    workflow["case_study_prompt"] = case_study_prompt

    # Update the timestamp because the workflow changed.
    workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

    return workflow

# Generate a case study draft using the collected workflow sources.
def generate_case_study_for_workflow(workflow_id: str) -> dict | None:
    workflow = workflows.get(workflow_id)

    # Return None if the workflow does not exist.
    if workflow is None:
        return None

    # Get the latest case study sources.
    case_study_sources = build_case_study_sources(workflow_id)

    # Make sure both the quote PDF and Fathom transcripts are available.
    if (
        not case_study_sources.get("quote_pdf_text")
        or not case_study_sources.get("fathom_transcripts")
    ):
        return None

    # Build the final prompt using the collected sources.
    case_study_prompt = build_case_study_prompt(case_study_sources)

    # Send the prompt to the AI and generate the six case study sections.
    case_study_sections = generate_case_study_draft(case_study_prompt)

    # Build a plain-text version for the local document file.
    case_study_draft = f"""Client Overview

{case_study_sections["client_overview"]}

Project Challenge

{case_study_sections["project_challenge"]}

COI Solution

{case_study_sections["coi_solution"]}

Products and Design Decisions

{case_study_sections["products_design"]}

Project Results

{case_study_sections["project_results"]}

Key Takeaways

{case_study_sections["key_takeaways"]}
"""

    # Save the generated case study draft as a document.
    case_study_document_path = save_case_study_document(
        client_name=workflow["client_name"],
        case_study_draft=case_study_draft,
    )

    # Store everything in the workflow.
    workflow["case_study_sources"] = case_study_sources
    workflow["case_study_prompt"] = case_study_prompt

    # Store the full plain-text draft.
    workflow["case_study_draft"] = case_study_draft

    # Store each section separately so Zapier can use them.
    workflow["client_overview"] = case_study_sections["client_overview"]
    workflow["project_challenge"] = case_study_sections["project_challenge"]
    workflow["coi_solution"] = case_study_sections["coi_solution"]
    workflow["products_design"] = case_study_sections["products_design"]
    workflow["project_results"] = case_study_sections["project_results"]
    workflow["key_takeaways"] = case_study_sections["key_takeaways"]

    workflow["case_study_document_path"] = case_study_document_path

    # The draft is now ready for someone to review.
    workflow["stage"] = WorkflowStage.READY_FOR_REVIEW
    workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

    return workflow

# Run the full case study workflow automatically.
def process_case_study_workflow(
    workflow_id: str,
    quote_pdf_path: str,
) -> dict | None:

    # Make sure the workflow exists.
    workflow = get_workflow(workflow_id)

    if workflow is None:
        return None

    # Extract and store the quote PDF information.
    add_quote_pdf_to_workflow(
        workflow_id,
        quote_pdf_path,
    )

    # Mark the workflow as validated.
    update_workflow_status(
        workflow_id,
        WorkflowStatus.VALIDATED,
    )

    # Search Fathom and collect the client transcripts.
    advance_to_fathom_search(workflow_id)

    # Generate the case study and Word document.
    completed_workflow = generate_case_study_for_workflow(
        workflow_id
    )

    return completed_workflow