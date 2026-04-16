from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import Settings
from app.keycrm import KeyCRMClient, KeyCRMError
from app.report import aggregate_products, format_report, split_message

LOGGER = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send /spisok to build the KeyCRM SKU summary.",
    )


async def spisok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return

    settings: Settings = context.application.bot_data["settings"]
    keycrm_client: KeyCRMClient = context.application.bot_data["keycrm_client"]

    source_chat_id = update.effective_chat.id
    target_chat_id = settings.telegram_target_chat_id or source_chat_id

    await context.bot.send_chat_action(chat_id=source_chat_id, action=ChatAction.TYPING)

    try:
        orders = await keycrm_client.fetch_orders()
        report = format_report(aggregate_products(orders))

        for chunk in split_message(report):
            await context.bot.send_message(chat_id=target_chat_id, text=chunk)

        if target_chat_id != source_chat_id:
            await context.bot.send_message(
                chat_id=source_chat_id,
                text=f"Report sent to chat {target_chat_id}.",
            )
    except KeyCRMError as error:
        LOGGER.exception("KeyCRM request failed")
        await context.bot.send_message(
            chat_id=source_chat_id,
            text=f"Failed to build report: {error}",
        )
    except Exception as error:  # pragma: no cover
        LOGGER.exception("Unexpected failure while building report")
        await context.bot.send_message(
            chat_id=source_chat_id,
            text=f"Unexpected error: {error}",
        )


def build_application(settings: Settings) -> Application:
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.bot_data["settings"] = settings
    application.bot_data["keycrm_client"] = KeyCRMClient(settings)
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("spisok", spisok_handler))
    return application
