""" Userbot module containing various translation. """

import os
import time
import asyncio
import shutil
from bs4 import BeautifulSoup
import re
from time import sleep
from html import unescape
from re import findall
from selenium import webdriver
from urllib.parse import quote_plus
from urllib.error import HTTPError
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError
from urbandict import define
from requests import get
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from gtts.lang import tts_langs
from emoji import get_emoji_regexp
from asyncio import sleep
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, CHROME_DRIVER, GOOGLE_CHROME_BIN
from userbot.events import register
from telethon.tl.types import DocumentAttributeAudio
from userbot.modules.upload_download import progress, humanbytes, time_formatter

LANG = "en"

@register(outgoing=True, pattern=r"^.tts(?: |$)([\s\S]*)")
async def text_to_speech(query):
    """ For .tts command, a wrapper for Google Text-to-Speech. """
    textx = await query.get_reply_message()
    message = query.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await query.edit(
            "`Give a text or reply to a message for Text-to-Speech!`")
        return

    try:
        gTTS(message, LANG)
    except AssertionError:
        await query.edit(
            'The text is empty.\n'
            'Nothing left to speak after pre-precessing, tokenizing and cleaning.'
        )
        return
    except ValueError:
        await query.edit('Language is not supported.')
        return
    except RuntimeError:
        await query.edit('Error loading the languages dictionary.')
        return
    tts = gTTS(message, LANG)
    tts.save("k.mp3")
    with open("k.mp3", "rb") as audio:
        linelist = list(audio)
        linecount = len(linelist)
    if linecount == 1:
        tts = gTTS(message, LANG)
        tts.save("k.mp3")
    with open("k.mp3", "r"):
        await query.client.send_file(query.chat_id, "k.mp3", voice_note=True)
        os.remove("k.mp3")
        if BOTLOG:
            await query.client.send_message(
                BOTLOG_CHATID, "Text to Speech executed successfully !")
        await query.delete()

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
        reply_text = translator.translate(deEmojify(message), dest=LANG)
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


@register(pattern=".lang (trt|tts) (.*)", outgoing=True)
async def lang(value):
    """ For .lang command, change the default langauge of userbot scrapers. """
    util = value.pattern_match.group(1).lower()
    if util == "trt":
        scraper = "Translator"
        global LANG
        arg = value.pattern_match.group(2).lower()
        if arg in LANGUAGES:
            LANG = arg
            LANG = LANGUAGES[arg]
        else:
            await value.edit(
                f"`Invalid Language code !!`\n`Available language codes for TRT`:\n\n`{LANGUAGES}`"
            )
            return
    elif util == "tts":
        scraper = "Text to Speech"
        global LANG
        arg = value.pattern_match.group(2).lower()
        if arg in tts_langs():
            LANG = arg
            LANG = tts_langs()[arg]
        else:
            await value.edit(
                f"`Invalid Language code !!`\n`Available language codes for TTS`:\n\n`{tts_langs()}`"
            )
            return
    await value.edit(f"`Language for {scraper} changed to {LANG.title()}.`")
    if BOTLOG:
        await value.client.send_message(
            BOTLOG_CHATID,
            f"`Language for {scraper} changed to {LANG.title()}.`")


def deEmojify(inputString):
    """ Remove emojis and other non-safe characters from string """
    return get_emoji_regexp().sub(u'', inputString)

CMD_HELP.update({
    'tts':
    '.tts <text> [or reply]\
        \nUsage: Translates text to speech for the language which is set.\nUse .lang tts <language code> to set language for tts. (Default is English.)'
})
CMD_HELP.update({
    'trt':
    '.trt <text> [or reply]\
        \nUsage: Translates text to the language which is set.\nUse .lang trt <language code> to set language for trt. (Default is English)'
})
