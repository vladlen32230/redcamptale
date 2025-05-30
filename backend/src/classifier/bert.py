import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer
from scipy.special import softmax
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
            self.speaker_session = None
            self.sprite_session = None
            self.speaker_tokenizer = None
            self.sprite_tokenizer = None
            self.initialized = True
    
    def load_model(self):
        """
        Load the quantized ONNX models and tokenizers for different tasks
        """
        
        speaker_model_path = "models_cache/speaker_quantized/onnx_model/model.onnx"
        sprite_model_path = "models_cache/sprite_quantized/onnx_model/model.onnx"
        
        # Model names for tokenizers
        speaker_model_name = "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33"
        sprite_model_name = "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33"
        
        # Configure ONNX Runtime for CPU with optimizations
        providers = ['CPUExecutionProvider']
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.intra_op_num_threads = 4
        session_options.inter_op_num_threads = 1
        
        # Load speaker model
        logger.info(f"Loading quantized speaker prediction model: {speaker_model_path}")
        self.speaker_session = ort.InferenceSession(
            speaker_model_path, 
            sess_options=session_options,
            providers=providers
        )
        self.speaker_tokenizer = AutoTokenizer.from_pretrained(speaker_model_name)
        
        # Load sprite model
        logger.info(f"Loading quantized sprite prediction model: {sprite_model_path}")
        self.sprite_session = ort.InferenceSession(
            sprite_model_path,
            sess_options=session_options, 
            providers=providers
        )
        self.sprite_tokenizer = AutoTokenizer.from_pretrained(sprite_model_name)
        
        logger.info("All quantized ONNX models loaded successfully!")

    def _onnx_zero_shot_classification(self, session, tokenizer, text, candidate_labels, hypothesis_template):
        """Perform zero-shot classification using ONNX model"""
        # Create premise-hypothesis pairs
        pairs = [(text, hypothesis_template.format(label)) for label in candidate_labels]
        
        # Tokenize
        batch_inputs = tokenizer(
            pairs, padding=True, truncation=True, max_length=512, return_tensors="np"
        )
        
        ort_inputs = {
            'input_ids': batch_inputs['input_ids'].astype(np.int64),
            'attention_mask': batch_inputs['attention_mask'].astype(np.int64)
        }
        
        # Run inference
        logits = session.run(None, ort_inputs)[0]
        entailment_scores = logits[:, 0]

        # Get probabilities and sort results
        probs = softmax(entailment_scores)
        sorted_indices = np.argsort(probs)[::-1]
        
        return {
            'labels': [candidate_labels[i] for i in sorted_indices],
            'scores': [float(probs[i]) for i in sorted_indices]
        }

    def _convert_messages_to_string(self, messages: list[Message]) -> str:
        return "\n[SEP]\n".join(f"{message.character}: {message.english_text}" for message in messages)

    def determine_next_speaking_character(
        self,
        messages: list[Message], 
        characters: list[Character]
    ) -> Character:
        history = self._convert_messages_to_string(reversed(messages)) + "\n[SEP]\n"
        if len(characters) == 1:
            return characters[0]

        candidate_labels = [character.value for character in characters]
        hypothesis_template = "The character {} is mentioned in the dialogue."
        
        result = self._onnx_zero_shot_classification(
            self.speaker_session, 
            self.speaker_tokenizer,
            history,
            candidate_labels,
            hypothesis_template
        )

        return str_to_enum(result['labels'][0], Character)

    def determine_next_chracter_sprite(
        self,
        chracter_name: Character,
        character_clothes: Clothes,
        messages: list[Message]
    ) -> CharacterSprite:
        history = self._convert_messages_to_string(messages)

        # Get character pose
        character_poses: tuple[Pose] = valid_character_poses[chracter_name]
        poses_descriptions = [pose.get_pose_description(pose) for pose in character_poses]

        hypothesis_template = f"The {chracter_name} mood based on his response is {{}}"
        
        result = self._onnx_zero_shot_classification(
            self.speaker_session,
            self.speaker_tokenizer,
            history,
            poses_descriptions,
            hypothesis_template
        )

        print(result)

        i = poses_descriptions.index(result['labels'][0])
        character_pose = character_poses[i]

        # Get character face
        face_expressions = valid_character_expressions[character_pose]
        face_expressions_descriptions = [face.get_facial_expression_description(face) for face in face_expressions]

        hypothesis_template = f"The {chracter_name} face expression based on response is {{}}"
        
        result = self._onnx_zero_shot_classification(
            self.sprite_session,
            self.sprite_tokenizer,
            history,
            face_expressions_descriptions,
            hypothesis_template
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

        candidate_labels = ["agreed to follow", "refused to follow"]
        hypothesis_template = f"The {character} {{}} {user_character_name} whether he wants to go."
        
        result = self._onnx_zero_shot_classification(
            self.speaker_session,
            self.speaker_tokenizer,
            history,
            candidate_labels,
            hypothesis_template
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

        hypothesis_template = "Mood of conversation is {}"
        
        result = self._onnx_zero_shot_classification(
            self.sprite_session,
            self.sprite_tokenizer,
            history,
            music_descriptions,
            hypothesis_template
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
