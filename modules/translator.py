""" Userbot module containing various translation. """

import os
from html import unescape
from re import findall
from shutil import rmtree
from urllib.error import HTTPError

from emoji import get_emoji_regexp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import LANGUAGES, Translator

from requests import get

from telethon.tl.types import DocumentAttributeAudio
from userbot import (BOTLOG, BOTLOG_CHATID, CMD_HELP, CHROME_DRIVER, GOOGLE_CHROME_BIN, bot)
from userbot.events import register

LANG = "en"

@register(outgoing=True, pattern=r"^.trt(?: |$)([\s\S]*)")
async def translateme(trans):
    """ For .trt command, translate the given text using Google Translate. """
    translator = Translator()
    textx = await trans.get_reply_message()
    message = trans.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await trans.edit("`Give a text or reply to a message to translate!`")
        return

    try:
        reply_text = translator.translate(deEmojify(message), dest=TRT_LANG)
    except ValueError:
        await trans.edit("Invalid destination language.")
        return

    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
    reply_text = f"From **{source_lan.title()}**\nTo **{transl_lan.title()}:**\n\n{reply_text.text}"

    await trans.edit(reply_text)
    if BOTLOG:
        await trans.client.send_message(
            BOTLOG_CHATID,
            f"Translated some {source_lan.title()} stuff to {transl_lan.title()} just now.",
        )


@register(pattern="^.lang (.*)", outgoing=True)
async def lang(value):
    """ For .lang command, change the default langauge of userbot scrapers. """
    global LANG
    LANG = value.pattern_match.group(1)
    await value.edit("Default language changed to **" + LANG + "**")
    if BOTLOG:
        await value.client.send_message(
            BOTLOG_CHATID, "Default language changed to **" + LANG + "**")

def deEmojify(inputString):
    """ Remove emojis and other non-safe characters from string """
    return get_emoji_regexp().sub(u'', inputString)

CMD_HELP.update({
    'trt':
    ".trt <text> or reply to someones text with .trt\n"
    "Usage: Translates text to the default language which is set."
})

CMD_HELP.update({
    'lang':
    ".lang <lang>\n"
    "Usage: Changes the default language of "
    "userbot translator used for Google Translate."
    
})
