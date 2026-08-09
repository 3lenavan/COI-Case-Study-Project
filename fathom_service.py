import os

import httpx
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

# Get the Fathom API key from the environment
FATHOM_API_KEY = os.getenv("FATHOM_API_KEY")

# Fathom endpoint used to retrieve meetings
FATHOM_MEETINGS_URL = "https://api.fathom.ai/external/v1/meetings"


# Get one page of meetings from Fathom
def get_meetings(cursor: str | None = None):
    headers = {
        "X-Api-Key": FATHOM_API_KEY
    }

    params = {}

    # If Fathom gave us a cursor, use it to request the next page
    if cursor is not None:
        params["cursor"] = cursor

    response = httpx.get(
        FATHOM_MEETINGS_URL,
        headers=headers,
        params=params,
        timeout=30.0,
    )

    # Raise an error if the request was unsuccessful
    response.raise_for_status()

    return response.json()


# Get multiple pages of meetings
# We are limiting it to 3 pages while testing
def get_all_meetings(max_pages: int = 3):
    all_meetings = []
    cursor = None
    page_count = 0

    while page_count < max_pages:
        data = get_meetings(cursor)

        page_count += 1

        print(f"\n========== PAGE {page_count} ==========")

        for meeting in data["items"]:
            print("Title:", meeting["title"])
            print("Recording ID:", meeting["recording_id"])
            print("Start Time:", meeting["recording_start_time"])
            print("-" * 40)

        all_meetings.extend(data["items"])

        cursor = data.get("next_cursor")

        if cursor is None:
            break

    return all_meetings


# Test the Fathom functions when this file is run directly
if __name__ == "__main__":
    meetings = get_all_meetings()

    print("\n========== SUMMARY ==========")
    print("Total meetings:", len(meetings))