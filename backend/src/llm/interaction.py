from src.schemas.database import Message
from src.llm.client import llm, model_name
from src.schemas.states.locations import Location
from src.schemas.states.characters import Character
from src.schemas.states.entities.base import Clothes
from src.schemas.states.times import Time
from src.llm.prompts import (
    message_summary_prompt, 
    character_message_prompt
)

async def get_summary_of_messages(messages: list[Message]) -> tuple[str, int, int]:
    interaction = "\n\n".join(
        f"{message.character}: {message.english_text}" for message in messages
    )
    
    summary = await llm.chat.completions.create(
        model="google/gemini-flash-1.5-8b",
        messages=[
            {"role": "system", "content": message_summary_prompt},
            {"role": "user", "content": interaction}
        ],
        top_p=0.95,
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
    messages: list[Message]
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

    response = await llm.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
        ],
        top_p=0.95,
        frequency_penalty=1.1,
        temperature=1.1
    )

    result_text = response.choices[0].message.content
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    
    return (result_text, input_tokens, output_tokens)