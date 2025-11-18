"""
Markdown formatter for Teams meeting transcripts
Optimized for Obsidian vault integration
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re


class ObsidianFormatter:
    """Formats Teams meeting data into Obsidian-friendly Markdown"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        return filename

    def format_meeting_metadata(self, meeting: Dict) -> str:
        """Format meeting metadata as Obsidian frontmatter"""
        metadata = []
        metadata.append("---")

        # Add tags
        metadata.append("tags:")
        metadata.append("  - teams/meeting")
        metadata.append("  - transcript")

        # Add meeting details
        if meeting.get('subject'):
            metadata.append(f"title: \"{meeting['subject']}\"")

        if meeting.get('start'):
            try:
                start_dt = datetime.fromisoformat(meeting['start'].replace('Z', '+00:00'))
                metadata.append(f"date: {start_dt.strftime('%Y-%m-%d')}")
                metadata.append(f"time: {start_dt.strftime('%H:%M')}")
            except:
                pass

        if meeting.get('organizer'):
            metadata.append(f"organizer: \"{meeting['organizer']}\"")

        metadata.append("type: teams-meeting")
        metadata.append("---")
        metadata.append("")

        return "\n".join(metadata)

    def format_transcript_content(self, transcript_lines: List[Dict]) -> str:
        """
        Format transcript content from parsed VTT/SRT or API data
        Expected format: [{'speaker': 'Name', 'timestamp': '00:01:23', 'text': '...'}]
        """
        if not transcript_lines:
            return ""

        content = []
        content.append("## Transcript")
        content.append("")

        current_speaker = None

        for line in transcript_lines:
            speaker = line.get('speaker', 'Unknown')
            timestamp = line.get('timestamp', '')
            text = line.get('text', '').strip()

            if not text:
                continue

            # Group consecutive lines from same speaker
            if speaker != current_speaker:
                if current_speaker is not None:
                    content.append("")  # Blank line between speakers

                current_speaker = speaker
                content.append(f"**{speaker}** `{timestamp}`")
                content.append(f"> {text}")
            else:
                content.append(f"> {text}")

        return "\n".join(content)

    def format_simple_transcript(self, transcript_text: str) -> str:
        """Format a simple transcript text (when no speaker/timestamp data available)"""
        if not transcript_text:
            return ""

        content = []
        content.append("## Transcript")
        content.append("")
        content.append(transcript_text)

        return "\n".join(content)

    def create_meeting_note(
        self,
        meeting: Dict,
        transcript_content: Optional[str] = None,
        transcript_lines: Optional[List[Dict]] = None,
        additional_notes: Optional[str] = None
    ) -> str:
        """Create a complete Obsidian note for a meeting"""

        note = []

        # Add frontmatter
        note.append(self.format_meeting_metadata(meeting))

        # Add title
        subject = meeting.get('subject', 'Untitled Meeting')
        note.append(f"# {subject}")
        note.append("")

        # Add meeting details
        note.append("## Meeting Details")
        note.append("")

        if meeting.get('start'):
            try:
                start_dt = datetime.fromisoformat(meeting['start'].replace('Z', '+00:00'))
                note.append(f"- **Date:** {start_dt.strftime('%Y-%m-%d')}")
                note.append(f"- **Time:** {start_dt.strftime('%H:%M %Z')}")
            except:
                note.append(f"- **Start:** {meeting.get('start')}")

        if meeting.get('end'):
            try:
                end_dt = datetime.fromisoformat(meeting['end'].replace('Z', '+00:00'))
                note.append(f"- **End Time:** {end_dt.strftime('%H:%M %Z')}")
            except:
                note.append(f"- **End:** {meeting.get('end')}")

        if meeting.get('organizer'):
            note.append(f"- **Organizer:** {meeting['organizer']}")

        note.append("")

        # Add notes section
        note.append("## Notes")
        note.append("")
        if additional_notes:
            note.append(additional_notes)
        else:
            note.append("*Add your notes here*")
        note.append("")

        # Add transcript
        if transcript_lines:
            note.append(self.format_transcript_content(transcript_lines))
        elif transcript_content:
            note.append(self.format_simple_transcript(transcript_content))
        else:
            note.append("## Transcript")
            note.append("")
            note.append("*Transcript not available or not yet imported*")
            note.append("")
            note.append("To add transcript:")
            note.append("1. Download transcript from Teams (Meeting > ... > Download transcript)")
            note.append("2. Use `parse_vtt.py` to convert VTT to structured format")
            note.append("3. Paste formatted content below")

        note.append("")

        # Add action items section
        note.append("## Action Items")
        note.append("")
        note.append("- [ ] ")
        note.append("")

        # Add links section
        note.append("## Related")
        note.append("")
        note.append("*Link to related notes here*")
        note.append("")

        return "\n".join(note)

    def save_note(self, meeting: Dict, content: str) -> Path:
        """Save note to file"""
        # Create filename from date and subject
        try:
            start_dt = datetime.fromisoformat(meeting['start'].replace('Z', '+00:00'))
            date_prefix = start_dt.strftime('%Y-%m-%d')
        except:
            date_prefix = 'undated'

        subject = meeting.get('subject', 'untitled')
        filename = f"{date_prefix}_{self.sanitize_filename(subject)}.md"

        file_path = self.output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    def parse_vtt_content(self, vtt_content: str) -> List[Dict]:
        """
        Parse VTT (WebVTT) transcript content
        Returns list of transcript lines with speaker, timestamp, and text
        """
        lines = []
        vtt_lines = vtt_content.split('\n')

        i = 0
        while i < len(vtt_lines):
            line = vtt_lines[i].strip()

            # Look for timestamp line (e.g., "00:00:01.234 --> 00:00:05.678")
            if '-->' in line:
                timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2})', line)
                timestamp = timestamp_match.group(1) if timestamp_match else ''

                # Next line(s) should be the speaker and text
                i += 1
                if i < len(vtt_lines):
                    speaker_text = vtt_lines[i].strip()

                    # Try to extract speaker (format: "<v Speaker Name>Text" or just "Text")
                    speaker = 'Unknown'
                    text = speaker_text

                    # Check for <v Speaker> format
                    speaker_match = re.match(r'<v\s+([^>]+)>(.*)', speaker_text)
                    if speaker_match:
                        speaker = speaker_match.group(1).strip()
                        text = speaker_match.group(2).strip()
                    else:
                        # Check for "Speaker: Text" format
                        colon_match = re.match(r'^([^:]+):\s*(.*)', speaker_text)
                        if colon_match:
                            speaker = colon_match.group(1).strip()
                            text = colon_match.group(2).strip()

                    if text:
                        lines.append({
                            'speaker': speaker,
                            'timestamp': timestamp,
                            'text': text
                        })

            i += 1

        return lines

    def parse_srt_content(self, srt_content: str) -> List[Dict]:
        """
        Parse SRT subtitle format transcript
        Returns list of transcript lines
        """
        lines = []
        blocks = re.split(r'\n\s*\n', srt_content.strip())

        for block in blocks:
            block_lines = block.strip().split('\n')
            if len(block_lines) < 3:
                continue

            # First line is sequence number
            # Second line is timestamp
            timestamp_line = block_lines[1]
            timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2})', timestamp_line)
            timestamp = timestamp_match.group(1) if timestamp_match else ''

            # Remaining lines are text
            text_lines = block_lines[2:]
            text = ' '.join(text_lines).strip()

            # Try to extract speaker
            speaker = 'Unknown'
            speaker_match = re.match(r'^([^:]+):\s*(.*)', text)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                text = speaker_match.group(2).strip()

            if text:
                lines.append({
                    'speaker': speaker,
                    'timestamp': timestamp,
                    'text': text
                })

        return lines
