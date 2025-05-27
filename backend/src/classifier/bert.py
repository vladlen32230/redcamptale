from transformers import pipeline
from src.schemas.database import Message, CharacterSprite
from src.schemas.states.characters import Character
from src.schemas.states.music import Music
from src.schemas.states.entities.base import Pose
from src.auxiliary.state import valid_character_poses, valid_character_expressions
from src.schemas.states.entities.base import Clothes
from src.auxiliary.helper import str_to_enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DistilBertClassifier:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DistilBertClassifier, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.speaker_classifier = None
            self.sprite_classifier = None
            self.music_classifier = None
            self.initialized = True
    
    def load_model(self):
        """
        Load the zero-shot classification pipelines for different tasks
        """
        # Model for next speaker prediction
        speaker_model = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
        logger.info(f"Loading speaker prediction model: {speaker_model}")
        self.speaker_classifier = pipeline(
            "zero-shot-classification",
            model=speaker_model,
            device='cpu',
            use_fast=False,
            max_length=512
        )
        
        # Model for sprite prediction
        sprite_model = "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33"
        logger.info(f"Loading sprite prediction model: {sprite_model}")
        self.sprite_classifier = pipeline(
            "zero-shot-classification",
            model=sprite_model,
            device='cpu',
            use_fast=False,
            max_length=512
        )

        logger.info("All models loaded successfully!")

    def _convert_messages_to_string(self, messages: list[Message]) -> str:
        return "\n[SEP]\n".join(f"{message.character}: {message.english_text}" for message in messages)


    def determine_next_speaking_character(
        self,
        messages: list[Message], 
        characters: list[Character]
    ) -> Character:
        #dialogue history: A: ... \n\n B: ...
        history = self._convert_messages_to_string(reversed(messages)) + "\n[SEP]\n"
        if len(characters) == 1:
            return characters[0]

        result = self.speaker_classifier(
            history,
            candidate_labels=[character.value for character in characters],
            hypothesis_template=f"The character {{}} is mentioned in the dialogue."
        )

        return str_to_enum(result['labels'][0], Character)


    def determine_next_chracter_sprite(
        self,
        chracter_name: Character,
        character_clothes: Clothes,
        messages: list[Message]
    ) -> CharacterSprite:
        history = self._convert_messages_to_string(messages)

        #get character pose
        character_poses: tuple[Pose] = valid_character_poses[chracter_name]
        poses_descriptions = [pose.get_pose_description(pose) for pose in character_poses]

        result = self.sprite_classifier(
            history,
            candidate_labels=poses_descriptions,
            hypothesis_template=f"The {chracter_name} mood based on his response is {{}}"
        )

        i = poses_descriptions.index(result['labels'][0])
        character_pose = character_poses[i]

        #get character face
        face_expressions = valid_character_expressions[character_pose]
        face_expressions_descriptions = [face.get_facial_expression_description(face) for face in face_expressions]

        result = self.sprite_classifier(
            history,
            candidate_labels=face_expressions_descriptions,
            hypothesis_template=f"The {chracter_name} face expression based on response is {{}}"
        )

        i = face_expressions_descriptions.index(result['labels'][0])
        character_face = face_expressions[i]

        return CharacterSprite(
            character=chracter_name,
            pose=character_pose,
            facial_expression=character_face,
            clothes=character_clothes
        )


    def determine_following(
        self,
        character: Character,
        user_character_name: str,
        messages: list[Message]
    ) -> bool:
        history = self._convert_messages_to_string(reversed(messages))

        result = self.speaker_classifier(
            history,
            candidate_labels=["agreed to follow", "refused to follow"],
            hypothesis_template=f"The {character} {{}} {user_character_name} whether he wants to go."  
        )

        follow_score = None
        for label, score in zip(result['labels'], result['scores']):
            if label == "agreed to follow":
                follow_score = score
                break

        return follow_score is not None and follow_score > 0.975


    def determine_music(
        self,
        messages: list[Message],
        previous_music: Music = Music.NONE
    ) -> Music:
        history = self._convert_messages_to_string(reversed(messages))

        musics = [m for m in Music if m != Music.NONE]
        music_descriptions = [m.get_music_description(m) for m in musics]

        result = self.speaker_classifier(
            history,
            candidate_labels=music_descriptions,
            hypothesis_template=f"Mood of conversation is {{}}"
        )

        # Get the top score
        top_score = result['scores'][0]
        
        if top_score > 0.35:
            i = music_descriptions.index(result['labels'][0])
            music = musics[i]
        else:
            # Otherwise, return the previous music
            music = previous_music

        return music

# Create a singleton instance
classifier = DistilBertClassifier()
