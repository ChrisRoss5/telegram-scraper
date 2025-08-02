"""Global variables for the telegram scraper"""

# Global variables accessible throughout the application
client = None
config = None
transliteration_schema = None
base_dir = None


def initialize_globals(telegram_client, app_config, trans_schema, app_base_dir):
    """Initialize all global variables"""
    global client, config, transliteration_schema, base_dir
    client = telegram_client
    config = app_config
    transliteration_schema = trans_schema
    base_dir = app_base_dir
