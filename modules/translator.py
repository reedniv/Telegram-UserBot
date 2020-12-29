""" Userbot module containing various scrapers. """

import os
from html import unescape
from re import findall
from shutil import rmtree
from urllib.error import HTTPError

from emoji import get_emoji_regexp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from pytube.helpers import safe_filename
from requests import get

from telethon.tl.types import DocumentAttributeAudio
from userbot import (BOTLOG, BOTLOG_CHATID, CMD_HELP, CURRENCY_API
                     , CHROME_DRIVER, GOOGLE_CHROME_BIN, bot)
from userbot.events import register

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
        await query.edit("`Give a text or reply to a message for Text-to-Speech!`")
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
    reply_text = f"**Source ({source_lan.title()}):**" + f"__\n\n{message}\n__" + f"\n\n**Translation ({transl_lan.title()}):**" + f"__\n\n{reply_text.text}__"

    await trans.client.send_message(trans.chat_id, reply_text)
    await trans.delete()
    if BOTLOG:
        await trans.client.send_message(
            BOTLOG_CHATID,
            f"Translate query {message} was executed successfully",
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
    'tts':
    ".tts <text> or reply to someones text with .trt\n"
    "Usage: Translates text to speech for the default language which is set."
})

CMD_HELP.update({
    'trt':
    ".trt <text> or reply to someones text with .trt\n"
    "Usage: Translates text to the default language which is set."
})

CMD_HELP.update({
    'lang':
    ".lang <lang>\n"
    "Usage: Changes the default language of"
    "userbot scrapers used for Google TRT, "
    "TTS may not work."
})
