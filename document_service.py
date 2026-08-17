from pathlib import Path


# Folder where generated case study drafts will be saved.
OUTPUT_FOLDER = Path("generated_case_studies")


# Save a generated case study draft as a text file.
def save_case_study_document(
    client_name: str,
    case_study_draft: str,
) -> str:

    # Create the output folder if it does not already exist.
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    # Make the client name safer to use as a file name.
    safe_client_name = client_name.replace(" ", "_")

    # Create the file path.
    file_path = OUTPUT_FOLDER / f"{safe_client_name}_case_study.txt"

    # Save the AI-generated case study draft.
    file_path.write_text(
        case_study_draft,
        encoding="utf-8",
    )

    # Return the location of the saved document.
    return str(file_path)

# Test saving a case study document when this file is run directly.
if __name__ == "__main__":
    test_draft = """
Client Overview

Patriot Family Insurance is the client for the office renovation project.

Project Challenge

The client needs new furniture and workspace solutions.

COI Solution

COI proposed furniture and workspace solutions for the office.

Project Results

Project results are not yet available.
"""

    file_path = save_case_study_document(
        client_name="Patriot Family Insurance",
        case_study_draft=test_draft,
    )

    print("\n========== DOCUMENT TEST ==========")
    print(f"Case study saved to: {file_path}")