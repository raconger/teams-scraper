# Teams Meeting Transcript Scraper

A Python tool to extract Microsoft Teams meeting data and transcripts, then format them as Obsidian-compatible Markdown notes.

## Features

- 🔐 Secure authentication via Microsoft Graph API
- 📅 Fetch meetings within a specified date range
- 📝 Export meeting metadata to Markdown with Obsidian frontmatter
- 🗣️ Parse VTT/SRT transcript files into readable format
- 📋 Pre-formatted sections for notes, action items, and related links
- 🏢 Works with enterprise Microsoft 365 accounts

## Why This Approach?

Microsoft Teams doesn't provide direct API access to meeting transcripts for security and compliance reasons. This tool takes a hybrid approach:

1. **Automated**: Uses Microsoft Graph API to fetch meeting metadata (title, date, attendees, etc.)
2. **Manual**: Requires downloading transcripts from Teams UI (simple download button)
3. **Automated**: Converts downloaded VTT transcripts to Markdown format

This respects Microsoft's security model while still achieving the goal of getting data into Obsidian.

## Prerequisites

- Python 3.7 or higher
- Microsoft 365 account (work or school)
- Azure AD admin access (or IT department help) to register an app
- Microsoft Teams with meeting recording/transcription enabled

## Setup

### 1. Register Azure Application

You need to create an Azure AD application to authenticate with Microsoft Graph API. This is a one-time setup.

#### Option A: Do It Yourself

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations** > **New registration**

3. Configure your app:
   - **Name**: `Teams Transcript Scraper` (or any name you prefer)
   - **Supported account types**: Select "Accounts in this organizational directory only"
   - **Redirect URI**: Leave blank
   - Click **Register**

4. Note down these values (you'll need them):
   - **Application (client) ID**
   - **Directory (tenant) ID**

5. Create a client secret:
   - Go to **Certificates & secrets** > **New client secret**
   - **Description**: `Teams Scraper Secret`
   - **Expires**: Choose based on your security policy (6 months, 1 year, etc.)
   - Click **Add**
   - **⚠️ IMPORTANT**: Copy the secret **Value** immediately (you can't see it again!)

6. Grant API permissions:
   - Go to **API permissions** > **Add a permission** > **Microsoft Graph** > **Application permissions**
   - Add these permissions:
     - `Calendars.Read` - Read calendars in all mailboxes
     - `OnlineMeetings.Read.All` - Read online meeting details
     - `User.Read.All` - Read all users' full profiles
     - `Chat.Read.All` - Read all chat messages (optional, for chat transcripts)
     - `CallRecords.Read.All` - Read call records (optional)
   - Click **Add permissions**
   - **⚠️ CRITICAL**: Click **Grant admin consent for [Your Organization]**
   - Wait for admin approval if needed

#### Option B: Ask Your IT Department

If you don't have admin access, send this to your IT team:

> Hi IT Team,
>
> I need to create an Azure AD app registration to access my Teams meeting data via Microsoft Graph API for a personal productivity tool. I need the following:
>
> 1. A new App Registration named "Teams Transcript Scraper"
> 2. Application (not delegated) permissions: `Calendars.Read`, `OnlineMeetings.Read.All`, `User.Read.All`
> 3. Admin consent granted for these permissions
> 4. The Application (client) ID, Directory (tenant) ID, and a client secret
>
> This will allow me to programmatically export my meeting notes to my personal note-taking system.

### 2. Install Dependencies

```bash
# Clone or download this repository
cd teams-scraper

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Fill in your `.env` file:

```bash
CLIENT_ID=your_application_client_id_here
CLIENT_SECRET=your_client_secret_value_here
TENANT_ID=your_directory_tenant_id_here

# Optional: customize output directory
OUTPUT_DIR=./transcripts
```

⚠️ **Security Note**: Never commit `.env` to version control! It's already in `.gitignore`.

## Usage

### Fetch Meeting Metadata

Get meetings from the last 30 days:

```bash
python scrape_teams.py --days 30
```

Get meetings in a specific date range:

```bash
python scrape_teams.py --start-date 2024-01-01 --end-date 2024-01-31
```

Specify custom output directory:

```bash
python scrape_teams.py --days 30 --output ~/Documents/Obsidian/Meetings
```

Dry run (test without saving files):

```bash
python scrape_teams.py --days 30 --dry-run --verbose
```

### Add Transcripts to Meeting Notes

Because Microsoft doesn't expose transcripts directly through the API, you'll need to manually download them:

1. **Download transcript from Teams**:
   - Open the meeting in Teams
   - Click the **"..."** menu (More options)
   - Select **"Download transcript"** or **"Download recording transcript"**
   - Save the `.vtt` file

2. **Convert VTT to Markdown**:
   ```bash
   python parse_vtt.py path/to/transcript.vtt
   ```

3. **Copy to your meeting note**:
   - Open the generated Markdown file in your `transcripts/` folder
   - Replace the placeholder transcript section with the output from `parse_vtt.py`

### Batch Processing Transcripts

If you have many VTT files:

```bash
# Convert and save each one
for file in ~/Downloads/*.vtt; do
    python parse_vtt.py "$file" -o "./transcripts/$(basename "$file" .vtt)_transcript.md"
done
```

## Output Format

Generated Markdown files are optimized for Obsidian with:

### Frontmatter (YAML)
```yaml
---
tags:
  - teams/meeting
  - transcript
title: "Weekly Team Sync"
date: 2024-01-15
time: 10:00
organizer: "Jane Doe"
type: teams-meeting
---
```

### Structured Sections
- Meeting Details (date, time, organizer)
- Notes (for your manual notes)
- Transcript (formatted with speakers and timestamps)
- Action Items (checklist)
- Related (for linking to other notes)

### Transcript Format
```markdown
**John Smith** `00:01:23`
> Let's discuss the project timeline.
> I think we should move the deadline.

**Jane Doe** `00:01:45`
> That makes sense. I'll update the schedule.
```

## Advanced Usage

### Custom Date Ranges

Get meetings from a specific month:
```bash
python scrape_teams.py --start-date 2024-01-01 --end-date 2024-01-31
```

Get meetings from last week:
```bash
python scrape_teams.py --days 7
```

### Integration with Obsidian

1. Set output directory to your Obsidian vault:
   ```bash
   # In .env file
   OUTPUT_DIR=/path/to/Obsidian/Vault/Meetings
   ```

2. Or use symbolic link:
   ```bash
   ln -s /path/to/Obsidian/Vault/Meetings ./transcripts
   ```

3. Use Obsidian plugins to enhance:
   - **Dataview**: Query meetings by date, tags, or attendees
   - **Calendar**: Visualize meetings on a timeline
   - **Tasks**: Aggregate action items across all meetings

### Dataview Query Example

Create a note with this Dataview query to list all recent meetings:

```dataview
TABLE
  date as Date,
  time as Time,
  organizer as Organizer
FROM "Meetings"
WHERE type = "teams-meeting"
SORT date DESC
LIMIT 20
```

## Troubleshooting

### Authentication Errors

**Error**: "Authentication failed: invalid_client"
- **Solution**: Double-check your `CLIENT_ID`, `CLIENT_SECRET`, and `TENANT_ID` in `.env`
- Make sure the client secret hasn't expired

**Error**: "Insufficient privileges"
- **Solution**: Ensure admin consent was granted for API permissions
- Wait 5-10 minutes after granting consent for changes to propagate

### No Meetings Found

**Problem**: Script runs but finds 0 meetings
- **Check**: Verify you had Teams meetings in the specified date range
- **Check**: Ensure the Azure app has `Calendars.Read` and `OnlineMeetings.Read.All` permissions
- **Try**: Run with `--verbose` flag to see detailed API responses

### Transcript Not Available

**Problem**: Transcript section says "not available"
- **Reason**: Microsoft Graph API doesn't expose transcripts directly (by design)
- **Solution**: Download transcripts manually from Teams and use `parse_vtt.py`

### Large Company Restrictions

Some organizations restrict API access:

1. **App Registration Disabled**: Ask IT to register the app for you
2. **Permissions Blocked**: Request exception for read-only access to your own data
3. **Conditional Access**: May need to use delegated (user) flow instead of application flow

If application permissions don't work, we can modify the code to use delegated permissions with browser-based auth. Let me know if you need this!

## Security & Privacy

- ✅ Uses official Microsoft Graph API (not web scraping)
- ✅ Only accesses your own meeting data
- ✅ Credentials stored locally in `.env` (never transmitted except to Microsoft)
- ✅ No third-party services or data storage
- ⚠️ Keep `.env` file secure and never commit to git
- ⚠️ Client secrets expire - rotate regularly per your security policy

## Limitations

1. **Transcript Access**: Graph API doesn't provide direct transcript access. You must download VTT files manually from Teams UI.
2. **Recording Requirement**: Transcripts only exist if meetings were recorded and transcribed.
3. **Permissions**: Requires Azure AD admin consent (may need IT help).
4. **Rate Limits**: Graph API has rate limits (shouldn't be an issue for personal use).

## Roadmap

Potential future enhancements:

- [ ] Support for delegated auth (browser login) as alternative to app-only auth
- [ ] Automated download of transcripts via browser automation (Playwright/Selenium)
- [ ] Support for channel meetings in addition to calendar meetings
- [ ] Export attendee lists
- [ ] OCR for meeting chat screenshots
- [ ] Direct sync to Obsidian Daily Notes

## Contributing

This is a personal productivity tool, but contributions are welcome! Some ideas:

- Better error handling and retry logic
- Support for more transcript formats
- Alternative authentication methods
- Export to other note formats (Notion, Roam, etc.)

## License

MIT License - feel free to use and modify for your needs.

## Acknowledgments

- Microsoft Graph API documentation
- MSAL Python library
- Obsidian community for Markdown best practices

---

## Questions?

Common questions:

**Q: Is this against Microsoft's Terms of Service?**
A: No! This uses the official Microsoft Graph API with proper authentication. It's the legitimate way to access your data.

**Q: Can I use this with personal Microsoft accounts?**
A: No, this requires Microsoft 365 (work/school accounts). Personal accounts don't have Azure AD app registration.

**Q: Will this work for meetings I didn't organize?**
A: Yes, as long as you were an attendee and have access to the meeting details.

**Q: Can my company see that I'm doing this?**
A: IT admins can see the app registration and its permissions, but they can't see what data you've accessed (just like any other app you authorize).

**Q: What if I don't have Azure admin access?**
A: You'll need to ask your IT department to create the app registration and grant permissions. Share the "Option B" section with them.
