# University Notice Finder

University Notice Finder is an automated Python project that:

- Scrapes notices from multiple Sri Lankan university websites
- Stores notices in SQLite
- Sends alerts through Telegram and email
- Shows collected notices in a searchable Flask web dashboard

## Current Universities

- `RUSL` - Rajarata University of Sri Lanka
- `UOM` - University of Moratuwa
- `UOV` - University of Vavuniya
- `UOK` - University of Kelaniya

## Project Structure

```text
notice_project/
|- app.py                 # Flask dashboard
|- scraper.py             # Scraper + email + Telegram sender
|- bot.py                 # Telegram registration bot
|- view_db.py             # Print DB contents for quick inspection
|- start_services.sh      # Starts app, bot, and scraper together
|- notices.db             # SQLite database (auto-created/updated)
|- template/
|  |- index.html          # Dashboard UI template
|- .env                   # Secrets/config (not committed)
```

## Requirements

- Python `3.10+` recommended
- Internet access
- Telegram bot token
- Gmail account with App Password (for email alerts)

Install Python dependencies:

```bash
pip install flask requests beautifulsoup4 python-dotenv schedule python-telegram-bot
```

## Environment Variables

Create a `.env` file in the project root:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
TELEGRAM_TOKEN=your_telegram_bot_token
```

Notes:

- `EMAIL_PASSWORD` should be a Gmail App Password, not your normal account password.
- `TELEGRAM_TOKEN` is required for both `bot.py` and Telegram notice delivery in `scraper.py`.

## Database

The project uses `notices.db` with two tables:

- `notices`:
  - `id` (PK)
  - `university`
  - `title`
  - `link` (UNIQUE)
- `users`:
  - `id` (PK)
  - `name`
  - `university`
  - `email`
  - `telegram_id` (UNIQUE)

## Run the Project

### Option 1: Start Everything with One Command (Recommended)

```bash
chmod +x start_services.sh
./start_services.sh
```

This starts:

- Flask dashboard (`app.py`)
- Telegram bot (`bot.py`)
- Scraper loop (`scraper.py`)

Stop all services with `Ctrl+C`.

### Option 2: Start Services Manually

In separate terminals:

```bash
python3 app.py
python3 bot.py
python3 scraper.py
```

## How It Works

1. `scraper.py` checks source sites on a schedule.
2. New notices are inserted into SQLite (duplicate links are skipped).
3. For every new notice:
   - Email notification is sent.
   - Telegram message is sent to registered users of that university.
4. `app.py` serves the dashboard where users can filter by university and search notices.

## Telegram User Registration Flow

1. Open your bot in Telegram.
2. Send `/start`.
3. Enter your name.
4. Select your university.
5. Enter email or tap `Skip`.

Your details are saved in the `users` table and used for targeted notifications.

## Useful Commands

Inspect database contents:

```bash
python3 view_db.py
```

## Troubleshooting

- `TELEGRAM_TOKEN is missing in .env`
  - Add `TELEGRAM_TOKEN` to `.env`.
- `bot.py is already running`
  - Stop the existing bot process before starting again.
- No emails are sent
  - Verify `EMAIL_USER` and Gmail App Password.
- No Telegram notices are sent
  - Ensure users completed bot registration (`/start`) and selected the matching university code.


