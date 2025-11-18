"""
Microsoft Teams API Client for fetching meeting transcripts
"""
import requests
from datetime import datetime
from dateutil import parser
from typing import List, Dict, Optional
from config import Config


class TeamsClient:
    """Client for interacting with Microsoft Teams via Graph API"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.base_url = Config.GRAPH_API_ENDPOINT

    def _make_request(self, url: str, method: str = 'GET', params: dict = None) -> dict:
        """Make HTTP request to Graph API with error handling"""
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {e.response.text if e.response else 'No response'}")
            raise
        except Exception as e:
            print(f"Error making request to {url}: {e}")
            raise

    def get_user_id(self) -> str:
        """Get the current user's ID"""
        url = f"{self.base_url}/me"
        response = self._make_request(url)
        return response.get('id')

    def get_online_meetings(self, user_id: str, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Get online meetings for a user
        Note: This gets meetings where transcripts might be available
        """
        meetings = []

        # Get calendar events (meetings)
        url = f"{self.base_url}/users/{user_id}/calendar/events"

        # Build filter for date range
        filters = []
        if start_date:
            filters.append(f"start/dateTime ge '{start_date.isoformat()}'")
        if end_date:
            filters.append(f"end/dateTime le '{end_date.isoformat()}'")

        params = {
            '$top': 999,
            '$orderby': 'start/dateTime desc',
            '$select': 'subject,start,end,onlineMeeting,organizer,attendees,id'
        }

        if filters:
            params['$filter'] = ' and '.join(filters)

        try:
            response = self._make_request(url, params=params)
            events = response.get('value', [])

            # Filter for online meetings only
            for event in events:
                if event.get('onlineMeeting'):
                    meetings.append({
                        'id': event.get('id'),
                        'subject': event.get('subject', 'No Subject'),
                        'start': event.get('start', {}).get('dateTime'),
                        'end': event.get('end', {}).get('dateTime'),
                        'organizer': event.get('organizer', {}).get('emailAddress', {}).get('name', 'Unknown'),
                        'onlineMeeting': event.get('onlineMeeting')
                    })
        except Exception as e:
            print(f"Error fetching meetings: {e}")

        return meetings

    def get_call_records(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Get call records which may contain transcript information
        Note: Requires CallRecords.Read.All permission
        """
        call_records = []
        url = f"{self.base_url}/communications/callRecords"

        params = {'$top': 999}

        # Note: Call Records API has different filtering
        # We'll filter in memory for now

        try:
            response = self._make_request(url, params=params)
            records = response.get('value', [])

            for record in records:
                start_time_str = record.get('startDateTime')
                if start_time_str:
                    start_time = parser.parse(start_time_str)

                    # Filter by date range
                    if start_date and start_time < start_date:
                        continue
                    if end_date and start_time > end_date:
                        continue

                    call_records.append(record)

        except Exception as e:
            print(f"Warning: Could not fetch call records (may need additional permissions): {e}")

        return call_records

    def get_meeting_transcript(self, meeting_id: str) -> Optional[Dict]:
        """
        Get transcript for a specific meeting
        Note: This is a simplified approach - actual implementation depends on
        how transcripts are stored in your organization
        """
        try:
            # Try to get transcript from event
            url = f"{self.base_url}/me/events/{meeting_id}/instances"
            response = self._make_request(url)

            # Check for transcript attachments or links
            # This varies by organization configuration

            return response
        except Exception as e:
            print(f"Could not fetch transcript for meeting {meeting_id}: {e}")
            return None

    def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Get messages from a Teams chat (which may include meeting chats)"""
        messages = []
        url = f"{self.base_url}/chats/{chat_id}/messages"

        try:
            response = self._make_request(url)
            messages = response.get('value', [])
        except Exception as e:
            print(f"Error fetching chat messages: {e}")

        return messages

    def get_user_chats(self) -> List[Dict]:
        """Get all chats for the current user"""
        chats = []
        url = f"{self.base_url}/me/chats"

        params = {
            '$top': 999,
            '$expand': 'lastMessagePreview'
        }

        try:
            response = self._make_request(url, params=params)
            chats = response.get('value', [])
        except Exception as e:
            print(f"Error fetching chats: {e}")

        return chats

    def search_for_transcripts(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Search for meeting transcripts across various sources
        Returns a list of meetings with available transcript data
        """
        transcripts = []

        print("Fetching online meetings...")
        user_id = self.get_user_id()
        meetings = self.get_online_meetings(user_id, start_date, end_date)

        print(f"Found {len(meetings)} online meetings")

        # For each meeting, try to find associated transcript data
        for meeting in meetings:
            transcript_data = {
                'meeting': meeting,
                'transcript_content': None,
                'chat_messages': []
            }

            # Try to get meeting chat
            online_meeting_info = meeting.get('onlineMeeting', {})

            # Add to results even if we can't get full transcript
            # User can manually download transcripts and we'll format them
            transcripts.append(transcript_data)

        return transcripts
