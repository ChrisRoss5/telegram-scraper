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

## Command Line Options

The Telegram Scraper supports command-line flags to run without interactive prompts.

### Basic Usage

```bash
# Run with default settings (real-time mode)
python index.py

# Run in historical sync mode without prompts
python index.py --mode historical --no-prompts

# Run in real-time mode without prompts
python index.py --mode realtime --no-prompts
```

### Historical Sync Mode Options

```bash
# Historical sync with specific offset ID
python index.py --mode historical --offset-id 12345 --no-prompts

# Historical sync starting 100 messages before the latest (negative offset)
python index.py --mode historical --offset-id -100 --no-prompts

# Historical sync with stop count limit
python index.py --mode historical --stop-count 100 --no-prompts

# Historical sync with both offset and limit
python index.py --mode historical --offset-id 12345 --stop-count 100 --no-prompts

# Historical sync starting 50 messages back and processing 25 messages
python index.py --mode historical --offset-id -50 --stop-count 25 --no-prompts
```

#### Understanding Negative Offset IDs

When using negative offset IDs, the scraper calculates the actual starting point relative to the latest known message:

- If your latest message ID is 10000 and you use `--offset-id -100`, the scraper will start from message ID 9900
- This is useful for re-processing recent messages or catching up on messages you might have missed

### Command Line Arguments

- `--mode, -m`: Operating mode

  - `1` or `historical`: Historical Sync mode
  - `2` or `realtime`: Real-time Listening mode (default)

- `--offset-id, -o`: Starting message ID for historical sync (default: calculated from last message)

  - Positive values: Start from the specified message ID
  - Negative values: Start from (default_offset_id + negative_value), e.g., -100 starts 100 messages before the default offset

- `--stop-count, -s`: Maximum number of messages to process in historical sync (default: no limit)

- `--no-prompts, -n`: Run without interactive prompts (use defaults or provided flags)

### Usage Examples

```bash
# Interactive mode (original behavior)
python index.py

# Non-interactive real-time mode
python index.py -n

# Non-interactive historical sync from message ID 5000, process 50 messages
python index.py -m historical -o 5000 -s 50 -n

# Non-interactive historical sync starting 200 messages before latest
python index.py -m historical -o -200 -n

# Non-interactive historical sync with defaults
python index.py -m 1 -n

# Get help
python index.py --help
```

## Output

- `messages.json`: Contains all scraped message data
- `media/`: Downloaded media files from posts
- `media_in_comments/`: Downloaded media files from comments
