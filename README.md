# The Tucson Weekend — Automated Newsletter Agent

Automatically generate a curated Tucson weekend guide newsletter every Tuesday, sent via Beehiiv Thursday noon.

## What It Does

- 🕷️ **Crawls 5 event sources** (Eventbrite, Visit Tucson, Tucson Weekly, Rialto Theatre, Club Congress)
- 🎯 **Selects the best headline event** using intelligent scoring
- 🍽️ **Recommends restaurants, bars, and hidden gems** from a curated Airtable database
- ✍️ **Generates friendly, natural newsletter copy** using Claude
- 📧 **Creates a draft in Beehiiv** for your review
- 📅 **Runs automatically every Tuesday at 8:03 AM** Arizona time
- 👤 **Respects venue cooldowns** (8 weeks for restaurants/bars, 12 weeks for hidden gems) to prevent repetition

## System Architecture

```
Event Crawlers (5 sources)
    ↓
[Deduplicate & Store in Airtable]
    ↓
[Select Headline Event + Venues]
    ↓
[Generate Content via Claude]
    ↓
[Render Email-Safe HTML]
    ↓
[Create Draft in Beehiiv]
    ↓
You review → Schedule Thursday noon
```

## Quick Start

### 1. Install Dependencies
```bash
cd ~/tucson-weekend-guide
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up Airtable (One-time)
```bash
python airtable/setup.py
```

This creates all required fields on your Airtable base (Venues, Events, Newsletter Drafts tables).

### 3. Seed the Venues Database
Go to your Airtable and add 10+ venues:
- At least 8 restaurants (Category: Restaurant)
- At least 4 bars (Category: Bar)
- At least 3 hidden gems (Category: Under the Radar)

For each venue, fill in:
- Name
- Category (Restaurant/Bar/Under the Radar)
- Cuisine/Vibe
- Neighborhood
- Address
- **One-liner** (critical — used in newsletter)
- Check Active = true

### 4. Test Locally
```bash
# Dry run (prints HTML, no Beehiiv push)
DRY_RUN=1 python main.py

# Full test (creates draft in Beehiiv)
python main.py
```

Verify:
- Log output looks good
- Draft appears in Beehiiv
- Content reads naturally

### 5. Register the Remote Cron
Once tested, set up automatic execution every Tuesday 8:03 AM Arizona time. Use Claude Code's `schedule` skill or RemoteTrigger API.

## Configuration

All settings in `config.py`:
- **RESTAURANTS_TO_SELECT**: 3
- **BARS_TO_SELECT**: 1
- **DEFAULT_COOLDOWN_WEEKS_NORMAL**: 8
- **DEFAULT_COOLDOWN_WEEKS_UNDER_RADAR**: 12

API keys stored in `.env` (gitignored):
- Airtable PAT
- Beehiiv API key + publication ID
- Eventbrite, Google Places, Yelp API keys

## File Structure

```
├── main.py                 # Pipeline orchestrator
├── config.py              # Configuration & credentials
├── airtable/              # Airtable REST client
├── crawlers/              # Event source crawlers (5 implementations)
├── selection/             # Headline & venue selection logic
├── content/               # Claude generation + HTML rendering
├── beehiiv/               # Beehiiv API client
├── logs/                  # Runtime logs
└── SETUP_GUIDE.md         # Detailed setup instructions
```

## How It Works

### Event Crawling
Crawls in priority order:
1. **Eventbrite API** — structured, reliable
2. **Visit Tucson** — official calendar
3. **Tucson Weekly** — community listings
4. **Rialto Theatre** — venue direct
5. **Club Congress** — venue direct

Events deduplicated by source ID before storage.

### Venue Selection
- Queries active venues from Airtable
- Filters by cooldown (weeks since last featured)
- Randomly selects from eligible pools
- Fallback: halves cooldown if not enough venues available

### Content Generation
Five separate Claude API calls:
1. Headline event introduction
2. Restaurant picks (3 paragraphs)
3. Bar picks (1–2 paragraphs)
4. Under the radar hidden gem
5. Email subject line

All with a consistent tone: friendly knowledgeable neighbor, confident but not pretentious.

### Beehiiv Draft
Created with:
- Inline CSS only (email-safe)
- Semantic HTML structure
- Thumbnail image from headline event
- Status: "draft" (you schedule manually)

### Airtable Tracking
After each run:
- Events marked as featured (with issue date)
- Venues marked as featured + cooldown updated
- Newsletter Drafts record created

## Logging

Each run creates a timestamped log in `logs/YYYY-MM-DD.log`:
- Crawl results
- Event selection
- Content generation
- Beehiiv draft URL

## Troubleshooting

**No events found?** → Event sources may be slow season or crawler broke. Check the log for details.

**Insufficient venues?** → You need to seed at least 10 venues in Airtable first.

**Beehiiv authentication failed?** → Verify API key in `.env`

**Scraper returns 0 events?** → Website structure may have changed. Check error logs; may need CSS selector updates.

## Next Steps

- [ ] Run `python airtable/setup.py`
- [ ] Add 10+ venues to Airtable
- [ ] Test with `DRY_RUN=1 python main.py`
- [ ] Test full run with `python main.py`
- [ ] Register remote cron trigger for automatic Tuesday runs

## License

Private project.
