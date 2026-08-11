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

# Get transcripts for a list of meetings
def get_transcripts_for_meetings(meetings: list):
    meetings_with_transcripts = []

    for meeting in meetings:
        recording_id = meeting["recording_id"]

        try:
            transcript = get_transcript(recording_id)
            meeting["transcript"] = transcript

        except httpx.HTTPStatusError:
            meeting["transcript"] = None
            meeting["transcript_error"] = "Transcript could not be retrieved"

        meetings_with_transcripts.append(meeting)

    return meetings_with_transcripts

# Format the transcripts for AI processing
def format_transcripts_for_ai(meetings: list) -> str:
    formatted_text = ""

    for meeting in meetings:
        formatted_text += f"\nMeeting: {meeting['title']}\n"
        formatted_text += f"Date: {meeting['recording_start_time']}\n"
        formatted_text += "-" * 40 + "\n"

        transcript_data = meeting.get("transcript")

        if transcript_data is None:
            formatted_text += "Transcript unavailable.\n"
            continue

        for section in transcript_data["transcript"]:
            speaker = section["speaker"]["display_name"]
            timestamp = section["timestamp"]
            text = section["text"]

            formatted_text += (
                f"{speaker} [{timestamp}]:\n"
                f"{text}\n\n"
            )

    return formatted_text

# Testing block to demonstrate the functionality of the Fathom service functions
if __name__ == "__main__":
    matching_meetings = find_meetings_by_client("Patriot")

    meetings_with_transcripts = get_transcripts_for_meetings(
        matching_meetings
    )

    formatted_transcripts = format_transcripts_for_ai(
        meetings_with_transcripts
    )

    print("\n========== AI TRANSCRIPT FORMAT TEST ==========")

    print(formatted_transcripts[:3000])