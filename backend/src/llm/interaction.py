from src.schemas.database import Message
from src.llm.client import llm_client, standard_model_name, premium_model_name
from src.schemas.states.locations import Location
from src.schemas.states.characters import Character
from src.schemas.states.entities.base import Clothes
from src.schemas.states.times import Time
import os
from src.llm.prompts import (
    message_summary_prompt, 
    character_message_prompt
)

async def get_summary_of_messages(messages: list[Message], use_premium=False) -> tuple[str, int, int]:
    interaction = "\n\n".join(
        f"{message.character}: {message.english_text}" for message in messages
    )
    
    if use_premium:
        summary = await llm_client.chat.completions.create(
            model=os.environ["PREMIUM_HELPER_MODEL_NAME"],
            messages=[
                {"role": "system", "content": message_summary_prompt},
                {"role": "user", "content": interaction}
            ],
            top_p=0.95,
            max_completion_tokens=512
        )
    else:
        summary = await llm_client.chat.completions.create(
            model=os.environ["STANDARD_HELPER_MODEL_NAME"],
            messages=[
                {"role": "system", "content": message_summary_prompt},
                {"role": "user", "content": interaction}
            ],
            top_p=0.95,
            max_completion_tokens=512
        )

    result_text = summary.choices[0].message.content
    input_tokens = summary.usage.prompt_tokens
    output_tokens = summary.usage.completion_tokens

    return (result_text, input_tokens, output_tokens)

async def get_character_message(
    character_name: Character,
    other_character_location: list[Character],
    location: Location,
    name_of_main_character: str,
    time_of_day: Time,
    biography_of_main_character: str,
    clothes: Clothes,
    previous_history: str,
    messages: list[Message],
    use_premium=False
) -> tuple[str, int, int]:
    interaction = "\n\n".join(
        f"{name_of_main_character if message.character == Character.MAIN_CHARACTER else message.character}: {message.english_text}"
        for message in reversed(messages)
    )

    time_of_day_description = time_of_day.get_time_description(time_of_day)

    character_description = character_name.get_character_description(character_name)
    location_description = location.get_description(location)
    clothes_description = clothes.get_clothes_description(clothes)
    other_character_location_descriptions = [
        c.get_character_description(c) for c in other_character_location if c != character_name
    ]
    other_characters_descriptions = [
        c.get_character_description(c) for c in Character if c not in [character_name, Character.MAIN_CHARACTER] and c not in other_character_location
    ]

    system_prompt = character_message_prompt.format(
        character_name=character_name.value,
        character_description=character_description,
        location_description=location_description,
        clothes_description=clothes_description,
        other_character_location_descriptions="\n".join(other_character_location_descriptions),
        other_characters_descriptions="\n".join(other_characters_descriptions),
        previous_history=previous_history,
        interaction=interaction,
        name_of_main_character=name_of_main_character,
        biography_of_main_character=biography_of_main_character,
        time_of_day=time_of_day_description
    )

    if use_premium:
        response = await llm_client.chat.completions.create(
            model=premium_model_name,
            messages=[
                {"role": "system", "content": system_prompt},
            ],
            top_p=0.9,
            temperature=1.1,
            max_completion_tokens=256
        )
    else:
        response = await llm_client.chat.completions.create(
            model=standard_model_name,
            messages=[
                {"role": "system", "content": system_prompt},
            ],
            top_p=0.95,
            frequency_penalty=1.1,
            temperature=1.1,
            max_completion_tokens=256,
        )

    result_text = response.choices[0].message.content
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    
    return (result_text, input_tokens, output_tokens)