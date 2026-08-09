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


# Search for meetings that contain the client name in their title
def find_meetings_by_client(client_name: str):
    meetings = get_all_meetings()

    matching_meetings = []

    for meeting in meetings:
        title = meeting["title"]

        if client_name.lower() in title.lower():
            matching_meetings.append(meeting)

    return matching_meetings


# Get the transcript for a specific recording
def get_transcript(recording_id: int):
    headers = {
        "X-Api-Key": FATHOM_API_KEY
    }

    transcript_url = (
        f"https://api.fathom.ai/external/v1/recordings/"
        f"{recording_id}/transcript"
    )

    response = httpx.get(
        transcript_url,
        headers=headers,
        timeout=30.0,
    )

    response.raise_for_status()

    return response.json()


# Test searching for meetings by client name
if __name__ == "__main__":
    matching_meetings = find_meetings_by_client("Patriot")

    print("\n========== MATCHING MEETINGS ==========")

    for meeting in matching_meetings:
        print("Title:", meeting["title"])
        print("Recording ID:", meeting["recording_id"])
        print("Start Time:", meeting["recording_start_time"])
        print("-" * 40)

    print("Total matches:", len(matching_meetings))

    transcript = get_transcript(171394681)

    print("\n========== TRANSCRIPT TEST ==========")

    for section in transcript["transcript"]:
        print("Speaker:", section["speaker"]["display_name"])
        print("Timestamp:", section["timestamp"])
        print("Text:", section["text"])
        print("-" * 40)