"""
Twitter Publisher API Integration.
Reads the TwitterThreadDraft and posts it as a connected thread.
"""

import os
import tweepy
import logging
from dotenv import load_dotenv

load_dotenv("backend/.env")
logger = logging.getLogger(__name__)

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

def post_to_twitter(draft_data: dict) -> list[str]:
    """Posts the parsed TwitterThreadDraft JSON as a connected thread."""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        logger.error("❌ Twitter API Keys are missing in .env!")
        return []

    try:
        # Initialize Tweepy Client (OAuth 1.0a)
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )

        tweets = []
        if "hook_tweet" in draft_data:
            tweets.append(draft_data["hook_tweet"])
        if "body_tweets" in draft_data:
            tweets.extend(draft_data["body_tweets"])
        if "conclusion_tweet" in draft_data:
            tweets.append(draft_data["conclusion_tweet"])

        if not tweets:
            logger.warning("No tweets found in draft.")
            return []

        published_ids = []
        previous_tweet_id = None

        logger.info(f"🐦 Publishing Twitter Thread ({len(tweets)} tweets)...")

        for idx, tweet_text in enumerate(tweets):
            if idx == 0:
                response = client.create_tweet(text=tweet_text)
                previous_tweet_id = response.data['id']
            else:
                response = client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=previous_tweet_id
                )
                previous_tweet_id = response.data['id']
            
            published_ids.append(previous_tweet_id)
            logger.info(f"✅ Tweet {idx+1}/{len(tweets)} posted! ID: {previous_tweet_id}")

        return published_ids

    except Exception as e:
        logger.error(f"❌ Failed to publish to Twitter: {str(e)}")
        return []
