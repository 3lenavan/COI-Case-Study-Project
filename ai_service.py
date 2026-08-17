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

IMPORTANT RULES:
- Use only facts that are explicitly supported by the provided sources.
- Do not invent, assume, estimate, exaggerate, or fill in missing information.
- Focus only on information relevant to the client's office project and case study.
- Ignore greetings, casual conversation, scheduling, emails, contact information, meeting setup, financing administration, and unrelated administrative discussion.
- Do not include personal email addresses or unnecessary personal information.

- Use the quote PDF primarily for products, quantities, pricing, project scope, and quoted services.
- Use the Fathom transcripts primarily for client needs, project challenges, design discussions, requested changes, project goals, and scope decisions.

- Do not invent project results, percentages, benefits, client reactions, or completion status.
- Do not claim the project was completed unless the sources explicitly confirm completion.
- Do not describe the client as "leading", "successful", "growing", or similar unless the sources explicitly support that description.

- Refer to Commercial Office Interiors as COI.
- Every section must contain a response.
- If there is not enough supported information for a section, clearly state that the information was not provided.

- Preserve the exact meaning of quantities, limits, capacities, and headcounts.
- When multiple numbers are mentioned for the same topic, do not combine them into a range unless the sources explicitly describe them as a range.
- Explain what each number represents. For example, distinguish between desired headcount, proposed workstation capacity, current seating, and maximum building occupancy.
- If later information updates or changes an earlier number or decision, describe the change instead of treating both statements as simultaneously final.

- Preserve whether something is confirmed, proposed, optional, recommended, being considered, or pending.
- Do not turn an option, recommendation, or possibility into a confirmed project decision.
- If a product or service is pending pricing, site evaluation, design review, client approval, or another decision, describe it as pending.

- Use the exact product or solution terminology supported by the sources.
- Do not convert a general concept into a specific product. For example, "sound masking" or general acoustic discussions must not become "acoustic panels" unless acoustic panels are explicitly mentioned.
- Do not combine unrelated facts. For example, VESA mounts apply to monitors and must not be associated with glass.
- Only include a product, service, or design feature if the sources explicitly mention it.

For each section:

Client Overview:
Briefly identify the client and project. Do not include contact information.

Project Challenge:
Describe the client's actual workspace needs, furniture needs, occupancy or headcount goals, layout concerns, acoustics, technology, growth plans, or other project-related challenges supported by the sources.
Preserve the exact meaning of every number mentioned.
If multiple capacities or headcounts were discussed, explain what each number represents rather than combining them into one range.

COI Solution:
Describe only solutions COI explicitly proposed, discussed, quoted, recommended, or provided.
Clearly distinguish confirmed solutions from optional or pending ideas.

Products and Design Decisions:
Include only products, quantities, furniture, layouts, finishes, and design choices explicitly supported by the sources.
Clearly label optional, proposed, or pending items instead of presenting them as final decisions.

Project Results:
Only describe confirmed outcomes.
If the project has not been completed or documented results are unavailable, state that clearly.

Key Takeaways:
Summarize the most important supported facts about the project.
Do not repeat scheduling, email, financing, or administrative details.
Do not introduce new information that was not already supported in the other sections.

COI Solution:
Describe only solutions COI proposed, discussed, quoted, or provided.

Products and Design Decisions:
Include relevant products, quantities, furniture, layouts, finishes, and design choices supported by the sources.

Project Results:
Only describe confirmed outcomes. If the project has not been completed or results are unavailable, say so.

Key Takeaways:
Summarize the most important supported facts about the project. Do not repeat scheduling or administrative details.

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
                "temperature": 0.1,
                "num_ctx": 32768
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