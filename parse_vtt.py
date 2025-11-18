#!/usr/bin/env python3
"""
Parse Teams VTT/SRT transcript files and convert to Markdown format
Useful for manually downloaded transcripts
"""
import argparse
import sys
from pathlib import Path
from markdown_formatter import ObsidianFormatter


def main():
    parser = argparse.ArgumentParser(
        description='Parse Teams VTT/SRT transcript file and convert to Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse VTT file and print to stdout
  python parse_vtt.py transcript.vtt

  # Parse and save to file
  python parse_vtt.py transcript.vtt -o formatted_transcript.md

  # Parse SRT file
  python parse_vtt.py transcript.srt
        """
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Path to VTT or SRT transcript file'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file (if not specified, prints to stdout)'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['vtt', 'srt', 'auto'],
        default='auto',
        help='Input file format (default: auto-detect)'
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return 1

    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Auto-detect format
    file_format = args.format
    if file_format == 'auto':
        if input_path.suffix.lower() == '.vtt' or 'WEBVTT' in content[:100]:
            file_format = 'vtt'
        elif input_path.suffix.lower() == '.srt':
            file_format = 'srt'
        else:
            print("Warning: Could not auto-detect format, assuming VTT")
            file_format = 'vtt'

    # Parse transcript
    formatter = ObsidianFormatter(Path('.'))

    if file_format == 'vtt':
        transcript_lines = formatter.parse_vtt_content(content)
    else:
        transcript_lines = formatter.parse_srt_content(content)

    if not transcript_lines:
        print("Error: No transcript content found in file")
        return 1

    print(f"Parsed {len(transcript_lines)} transcript lines")

    # Format as markdown
    markdown_output = formatter.format_transcript_content(transcript_lines)

    # Output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        print(f"Saved to: {output_path}")
    else:
        print()
        print("=" * 60)
        print(markdown_output)
        print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
