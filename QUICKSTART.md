# Quick Start Guide

Get up and running in 5 steps!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Get Azure Credentials

You need three pieces of information from Azure Portal:

- **Client ID**: Your application ID
- **Client Secret**: Your application secret (create under "Certificates & secrets")
- **Tenant ID**: Your organization's directory ID

Don't have admin access? Send the template email in README.md to your IT team.

## 3. Configure

```bash
cp .env.example .env
# Edit .env with your credentials
```

## 4. Run

Fetch meetings from last 30 days:

```bash
python scrape_teams.py --days 30
```

## 5. Add Transcripts

For each meeting:

1. Download transcript from Teams (... menu → Download transcript)
2. Convert to Markdown: `python parse_vtt.py transcript.vtt`
3. Copy output into your meeting note

## What You Get

Each meeting becomes a Markdown file like this:

```
2024-01-15_Weekly_Team_Sync.md
├── Frontmatter (tags, date, metadata)
├── Meeting Details (time, organizer)
├── Notes (your editable notes)
├── Transcript (speaker-by-speaker)
├── Action Items (checklist)
└── Related (links to other notes)
```

Perfect for Obsidian! 📝

## Troubleshooting

- **No meetings found**: Check date range and API permissions
- **Auth failed**: Verify credentials in `.env`
- **Need help**: See full README.md for detailed troubleshooting

## Next Steps

- Set `OUTPUT_DIR` to your Obsidian vault path
- Create Dataview queries to aggregate meetings
- Link meetings to project notes
- Track action items across meetings

Happy note-taking! 🚀
