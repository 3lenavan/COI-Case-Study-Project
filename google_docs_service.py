import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Permission needed to create and edit Google Docs.
SCOPES = ["https://www.googleapis.com/auth/documents"]


# Connect to the Google Docs API.
def get_google_docs_service():
    credentials = None

    # Use the saved login token if one already exists.
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES,
        )

    # Log in again if there is no valid saved token.
    if not credentials or not credentials.valid:

        # Refresh the token if possible.
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        else:
            # Open the Google login page using credentials.json.
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )

            credentials = flow.run_local_server(port=0)

        # Save the login so we do not have to log in every time.
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    # Create the Google Docs API connection.
    service = build(
        "docs",
        "v1",
        credentials=credentials,
    )

    return service


# Create a Google Doc and add text to it.
def create_google_doc(
    title: str,
    content: str,
) -> str:

    service = get_google_docs_service()

    # Create the blank Google Doc.
    document = service.documents().create(
        body={
            "title": title
        }
    ).execute()

    document_id = document["documentId"]

    # Add the case study text to the document.
    requests = [
        {
            "insertText": {
                "location": {
                    "index": 1
                },
                "text": content,
            }
        }
    ]

    service.documents().batchUpdate(
        documentId=document_id,
        body={
            "requests": requests
        },
    ).execute()

    # Create the Google Doc link.
    document_url = (
        f"https://docs.google.com/document/d/{document_id}/edit"
    )

    return document_url


# Test creating a Google Doc with text.
if __name__ == "__main__":
    test_content = """
Client Overview

Patriot Family Insurance is the client for the Nashua Office Renovation project.

Project Results

Project results are not yet available.
"""

    document_url = create_google_doc(
        title="COI Case Study Google Docs Test",
        content=test_content,
    )

    print("\n========== GOOGLE DOCS TEST ==========")
    print(f"Document URL: {document_url}")