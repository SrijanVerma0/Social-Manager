"""
Telegram HITL (Human-In-The-Loop) Bot for Social Manager.
Commands:
/start - Welcomes the user.
/pending - Fetches the latest generated campaign and asks for approval.
"""

import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.campaign import Campaign
from backend.app.models.post import Post, PostStatus, PostPlatform

# Import our Publishers!
from backend.app.publishers.twitter_client import post_to_twitter
from backend.app.publishers.devto_client import post_to_devto
from backend.app.publishers.linkedin_client import post_to_linkedin

# Load environment variables
load_dotenv("backend/.env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! 👋\nI am your AI Social Manager Bot.\n"
        "Send /pending to review newly generated posts for publishing."
    )

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetches the latest Campaign and its posts from SQLite."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Campaign).order_by(Campaign.id.desc()).limit(1))
        campaign = result.scalar_one_or_none()

        if not campaign:
            await update.message.reply_text("No campaigns found in the database yet!")
            return

        posts_result = await session.execute(select(Post).where(Post.campaign_id == campaign.id))
        posts = posts_result.scalars().all()

        message = f"🔥 <b>New Campaign Generated:</b>\n"
        message += f"<b>Topic:</b> {campaign.topic}\n"
        message += f"<b>Critic Score:</b> {campaign.critic_score}/100\n"
        message += f"<b>Drafts Ready:</b> {len(posts)} platforms\n\n"
        message += "Do you want to APPROVE and Publish to all platforms?"

        keyboard = [
            [
                InlineKeyboardButton("✅ Approve & Publish", callback_data=f"approve_{campaign.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{campaign.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_html(text=message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles clicks on the Approve or Reject buttons."""
    query = update.callback_query
    await query.answer("Processing your request...") # Tell Telegram we received the click

    data = query.data
    action, campaign_id = data.split("_")

    if action == "approve":
        await query.edit_message_text(text=f"⚙️ Campaign {campaign_id} APPROVED! Publishing to platforms now... Please wait.")
        
        async with AsyncSessionLocal() as session:
            posts_result = await session.execute(select(Post).where(Post.campaign_id == int(campaign_id)))
            posts = posts_result.scalars().all()
            
            publish_logs = []
            
            for post in posts:
                # Only publish APPROVED posts
                if post.status != PostStatus.APPROVED:
                    continue
                    
                draft_dict = json.loads(post.content_text)
                
                # Twitter Publishing
                if post.platform == PostPlatform.TWITTER:
                    tweet_ids = post_to_twitter(draft_dict)
                    if tweet_ids:
                        post.status = PostStatus.PUBLISHED
                        publish_logs.append(f"✅ Twitter Thread Live! ({len(tweet_ids)} tweets)")
                    else:
                        publish_logs.append("❌ Twitter Publishing Failed.")
                
                # LinkedIn Publishing
                elif post.platform == PostPlatform.LINKEDIN:
                    linkedin_id = await post_to_linkedin(draft_dict)
                    if linkedin_id:
                        post.status = PostStatus.PUBLISHED
                        publish_logs.append(f"✅ LinkedIn Post Live! (ID: {linkedin_id})")
                    else:
                        publish_logs.append("❌ LinkedIn Publishing Failed.")

                # Dev.to Blog Publishing
                elif post.platform == PostPlatform.BLOG:
                    devto_url = post_to_devto(draft_dict, publish_live=True)
                    if devto_url:
                        post.status = PostStatus.PUBLISHED
                        post.published_url = devto_url
                        publish_logs.append(f"✅ Dev.to Article Live! ({devto_url})")
                    else:
                        publish_logs.append("⚠️ Dev.to Publishing Skipped/Failed.")

                        
            # Save the new statuses to DB
            await session.commit()
            
            final_msg = f"🎉 <b>Campaign {campaign_id} Publishing Complete!</b>\n\n"
            final_msg += "\n".join(publish_logs)
            await query.message.reply_html(text=final_msg)

    elif action == "reject":
        await query.edit_message_text(text=f"❌ Campaign {campaign_id} REJECTED. It won't be published.")

from telegram.request import HTTPXRequest

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in .env!")
        return

    logger.info("Starting Telegram Bot...")
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    app = Application.builder().token(TELEGRAM_TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("pending", pending_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
