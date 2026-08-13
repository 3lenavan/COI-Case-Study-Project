# Build the prompt that will eventually be sent to the AI.
def build_case_study_prompt(case_study_sources: dict) -> str:

    # Get the project information from the collected case study sources.
    client_name = case_study_sources.get("client_name")
    project_name = case_study_sources.get("project_name")
    emanage_job_number = case_study_sources.get("emanage_job_number")

    # Get the information collected from Fathom and the quote PDF.
    fathom_transcripts = case_study_sources.get("fathom_transcripts")
    quote_pdf_text = case_study_sources.get("quote_pdf_text")

    # Build one prompt containing all of the information for the AI.
    prompt = f"""
Create a professional case study draft using the information provided below.

CLIENT:
{client_name}

PROJECT:
{project_name}

EMANAGE JOB NUMBER:
{emanage_job_number}

QUOTE PDF:
{quote_pdf_text}

FATHOM TRANSCRIPTS:
{fathom_transcripts}

Use only the information provided above.
Do not invent information that is not supported by the sources.

Organize the case study into these sections:

1. Client Overview
2. Project Challenge
3. COI Solution
4. Products and Design Decisions
5. Project Results
6. Key Takeaways
"""

    return prompt