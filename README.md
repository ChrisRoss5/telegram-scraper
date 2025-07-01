# Custom Telegram Scraper

A Python script to scrape messages, media, and comments from a specific Telegram channel using the Telethon library.

## Features

- Downloads all messages from a Telegram channel
- Saves message metadata (sender info, reactions, views, forwards)
- Downloads media files (videos, audio, images)
- Scrapes comments/replies to messages
- Handles forwarded messages and polls
- Saves data to JSON format

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Configure your Telegram API credentials in `config.json`:

   - Copy and modify the config file with your credentials
   - `api_id`: Your Telegram API ID
   - `api_hash`: Your Telegram API hash
   - `channel_username`: Target channel username

3. Run the scraper:
   ```
   python index.py
   ```

## Output

- `messages.json`: Contains all scraped message data
- `media/`: Downloaded media files from posts
- `media_in_comments/`: Downloaded media files from comments
