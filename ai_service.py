import httpx

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

Use only facts that are explicitly supported by the information above.

IMPORTANT RULES:
- Do not invent, assume, or estimate any facts.
- Do not invent project results, percentages, benefits, or client reactions.
- Do not claim the project was completed unless the sources explicitly say it was completed.
- Do not describe the client using claims such as "leading", "successful", or "growing" unless the sources say so.
- Do not add products, services, design decisions, or project challenges that are not mentioned in the sources.
- Refer to Commercial Office Interiors as COI.
- If the sources do not provide enough information for a section, clearly state that the information was not provided instead of making something up.
- Every section must contain a response. If there is not enough supported information for a section, state that the information was not provided.

Organize the case study into these sections:

1. Client Overview
2. Project Challenge
3. COI Solution
4. Products and Design Decisions
5. Project Results
6. Key Takeaways
"""

    return prompt


# Send the completed case study prompt to the local Ollama AI model.
def generate_case_study_draft(case_study_prompt: str) -> str:

    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": case_study_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            },
        },
        timeout=120.0,
    )

    response.raise_for_status()

    response_data = response.json()

    return response_data["response"]


# Test the full prompt and local AI generation when this file is run directly.
if __name__ == "__main__":
    test_sources = {
        "client_name": "Patriot Family Insurance",
        "project_name": "Nashua Office Renovation",
        "emanage_job_number": "JOB-123",
        "quote_pdf_text": """
COI will provide:
- 4 private office desks
- 4 mobile file cabinets
- 1 conference room table
- 8 conference chairs
""",
        "fathom_transcripts": """
The client discussed needing new office furniture
and workspace solutions for their Nashua office.
"""
    }

    # Build the same prompt the real workflow will use.
    test_prompt = build_case_study_prompt(test_sources)

    # Send the prompt to the local Ollama model.
    draft = generate_case_study_draft(test_prompt)

    print("\n========== AI CASE STUDY TEST ==========")
    print(draft)