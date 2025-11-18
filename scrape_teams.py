#!/usr/bin/env python3
"""
Microsoft Teams Meeting Transcript Scraper
Exports meeting information to Obsidian-compatible Markdown files
"""
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dateutil import parser

from config import Config
from auth import GraphAuthenticator
from teams_client import TeamsClient
from markdown_formatter import ObsidianFormatter


def parse_date(date_string: str) -> datetime:
    """Parse date string in various formats"""
    try:
        return parser.parse(date_string)
    except Exception as e:
        raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD or similar.")


def main():
    parser_cli = argparse.ArgumentParser(
        description='Scrape Microsoft Teams meeting transcripts and export to Obsidian Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get meetings from the last 30 days
  python scrape_teams.py --days 30

  # Get meetings in a specific date range
  python scrape_teams.py --start-date 2024-01-01 --end-date 2024-01-31

  # Specify custom output directory
  python scrape_teams.py --days 30 --output ~/Documents/Obsidian/Meetings

  # Dry run (fetch but don't save)
  python scrape_teams.py --days 30 --dry-run
        """
    )

    # Date range options
    date_group = parser_cli.add_mutually_exclusive_group()
    date_group.add_argument(
        '--days',
        type=int,
        help='Number of days to look back from today (default: 30)',
        default=30
    )
    date_group.add_argument(
        '--start-date',
        type=str,
        help='Start date (YYYY-MM-DD format)'
    )

    parser_cli.add_argument(
        '--end-date',
        type=str,
        help='End date (YYYY-MM-DD format, defaults to today)',
        default=None
    )

    parser_cli.add_argument(
        '--output',
        type=str,
        help='Output directory for Markdown files (default: from config)',
        default=None
    )

    parser_cli.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch meetings but don\'t save files'
    )

    parser_cli.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser_cli.parse_args()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file based on .env.example and fill in your credentials.")
        print("See README.md for setup instructions.")
        return 1

    # Calculate date range
    if args.start_date:
        start_date = parse_date(args.start_date)
    else:
        start_date = datetime.now() - timedelta(days=args.days)

    if args.end_date:
        end_date = parse_date(args.end_date)
    else:
        end_date = datetime.now()

    # Set output directory
    output_dir = Path(args.output) if args.output else Config.OUTPUT_DIR

    print("=" * 60)
    print("Teams Meeting Transcript Scraper")
    print("=" * 60)
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Output directory: {output_dir}")
    print()

    # Authenticate
    print("Authenticating with Microsoft Graph API...")
    try:
        authenticator = GraphAuthenticator()
        access_token = authenticator.get_access_token()
        print("✓ Authentication successful")
        print()
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return 1

    # Initialize clients
    teams_client = TeamsClient(access_token)
    formatter = ObsidianFormatter(output_dir)

    # Fetch meetings
    print("Fetching meetings from Teams...")
    try:
        transcripts = teams_client.search_for_transcripts(start_date, end_date)
        print(f"✓ Found {len(transcripts)} meetings")
        print()
    except Exception as e:
        print(f"✗ Error fetching meetings: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Process and save meetings
    if not transcripts:
        print("No meetings found in the specified date range.")
        return 0

    print(f"Processing {len(transcripts)} meetings...")
    print()

    saved_count = 0
    for i, transcript_data in enumerate(transcripts, 1):
        meeting = transcript_data['meeting']
        subject = meeting.get('subject', 'Untitled')

        if args.verbose:
            print(f"[{i}/{len(transcripts)}] {subject}")

        try:
            # Create note content
            note_content = formatter.create_meeting_note(
                meeting=meeting,
                transcript_content=transcript_data.get('transcript_content'),
                transcript_lines=None  # Will be populated if transcripts are directly available
            )

            if not args.dry_run:
                file_path = formatter.save_note(meeting, note_content)
                if args.verbose:
                    print(f"    → Saved to: {file_path}")
                saved_count += 1
            else:
                if args.verbose:
                    print(f"    → Would save (dry-run mode)")

        except Exception as e:
            print(f"    ✗ Error processing meeting: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    print()
    print("=" * 60)
    if args.dry_run:
        print(f"Dry run complete. Would have saved {len(transcripts)} files.")
    else:
        print(f"✓ Successfully saved {saved_count} meeting notes to {output_dir}")
        print()
        print("Next steps:")
        print("1. Review the generated Markdown files")
        print("2. Download transcripts from Teams for each meeting:")
        print("   - Open meeting in Teams")
        print("   - Click '...' menu > Download transcript")
        print("3. Use parse_vtt.py to convert VTT transcripts to Markdown")
        print("4. Copy transcript content into the relevant meeting notes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
