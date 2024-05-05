import asyncio
from typing import List

from httpx import ConnectError
from loguru import logger
from voicevox import Speaker

from utils.llm.LlmFactory import LlmFactory
from utils.llm.LlmMessage import LlmMessage
from voicevox.client import Client
translation_llm = LlmFactory.get_llm_by_model_name("autodl-llama", system_prompt=[
    LlmMessage(role="system", content="把用户给出的内容翻译成日语。必须直接给出翻译结果，不允许回答多余的内容。")
])
speaker_info = None

async def tts_name_to_spearker(tts_name):
    info = await async_get_speaker_info()
    return info[tts_name]

async def async_get_speaker_info():
    global speaker_info
    if speaker_info is None:
        async with Client() as client:
            speaker_info = {}
            speakers: List[Speaker] = await client.fetch_speakers()
            for speaker in speakers:
                speaker_info[speaker.name] = speaker
    return speaker_info

async def async_to_japanese_tts_and_save(tts_name, content, save_path):
    translation_llm.clear_memory()
    japanese_content = translation_llm.chat(query=LlmMessage(content=content), max_new_tokens=512).content
    logger.info(f"日语内容：{japanese_content}")
    speaker = await tts_name_to_spearker(tts_name)
    async with Client() as client:
        audio_query = await client.create_audio_query(
            japanese_content, speaker=speaker.styles[0].id
        )
        with open(save_path, "wb") as f:
            f.write(await audio_query.synthesis(speaker=speaker.styles[0].id))

def to_japanese_tts_and_save(tts_name, content, save_path):
    asyncio.run(async_to_japanese_tts_and_save(tts_name, content, save_path))

def get_speaker_names():
    try:
        speakers = asyncio.run(async_get_speaker_info())
        return list(speakers.keys())
    except ConnectError:
        return []



