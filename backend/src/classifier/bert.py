import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from src.schemas.database import Message, CharacterSprite
from src.schemas.states.characters import Character
from src.schemas.states.music import Music
from src.schemas.states.entities.base import Pose
from src.auxiliary.state import valid_character_poses, valid_character_expressions
from src.schemas.states.entities.base import Clothes
from src.auxiliary.helper import str_to_enum
import logging
import os
import torch
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Classifier:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Classifier, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.session = None
            self.tokenizer = None
            self.initialized = True
    
    def load_model(self):
        """
        Load the model using transformers and convert to ONNX in memory for inference
        """
        
        # Model name for tokenizer and model
        model_name = os.environ["STANDARD_CLASSIFIER_NAME"]
        
        logger.info(f"Loading model from transformers: {model_name}")
        
        # Load tokenizer and model from transformers
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Set model to evaluation mode
        model.eval()
        
        # Create dummy inputs for export (premise-hypothesis pair)
        premise = "This is a sample premise text for ONNX export."
        hypothesis = "This is about exporting models."

        inputs = self.tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            max_length=512,
            padding="max_length",
            truncation=True
        )
        
        logger.info("Converting model to ONNX format in memory...")
        
        # Create a BytesIO buffer to hold the ONNX model in memory
        onnx_buffer = io.BytesIO()
        
        # Extract input names and create dynamic axes
        input_names = ['input_ids', 'attention_mask', 'token_type_ids']
        
        # Create inputs tuple in the same order as input_names
        export_inputs = (inputs['input_ids'], inputs['attention_mask'], inputs['token_type_ids'])
        
        dynamic_axes = {
            name: {0: "batch_size", 1: "sequence_length"} 
            for name in input_names
        }
        dynamic_axes["logits"] = {0: "batch_size"}
        
        # Export to ONNX with higher opset version for better compatibility
        with torch.no_grad():
            torch.onnx.export(
                model,
                export_inputs,
                onnx_buffer,
                input_names=input_names,
                output_names=["logits"],
                dynamic_axes=dynamic_axes,
                do_constant_folding=True,
                opset_version=14,  # Higher opset version for better DeBERTa support
                export_params=True,
                verbose=False
            )
        
        # Get the ONNX model bytes
        onnx_model_bytes = onnx_buffer.getvalue()
        
        # Configure ONNX Runtime for CPU with optimizations
        providers = ['CPUExecutionProvider']
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL  # Better for CPU
        session_options.intra_op_num_threads = 2
        session_options.inter_op_num_threads = 1
        
        # Load ONNX model from memory
        logger.info("Loading ONNX model from memory...")
        self.session = ort.InferenceSession(
            onnx_model_bytes, 
            sess_options=session_options,
            providers=providers
        )
        
        logger.info("Model loaded and converted to ONNX successfully!")

    def _onnx_zero_shot_classification(self, session, tokenizer, text, candidate_labels, hypothesis_template):
        """Perform zero-shot classification using ONNX model"""
        # Create premise-hypothesis pairs
        pairs = [(text, hypothesis_template.format(label)) for label in candidate_labels]
        
        batch_inputs = tokenizer(
            pairs, padding=True, truncation=True, max_length=256, return_tensors="np"
        )

        ort_inputs = {
            'input_ids': batch_inputs['input_ids'].astype(np.int64),
            'attention_mask': batch_inputs['attention_mask'].astype(np.int64)
        }
        
        # Run inference
        logits = session.run(None, ort_inputs)[0]
        entailment_scores = logits[:, 0]

        sorted_indices = np.argsort(entailment_scores)[::-1]
        
        return {
            'labels': [candidate_labels[i] for i in sorted_indices],
            'scores': [float(entailment_scores[i]) for i in sorted_indices]
        }

    def _convert_messages_to_string(self, messages: list[Message], include_character_name: bool = True) -> str:
        return "\n".join(
            f"{message.character}: {message.english_text}" 
            if include_character_name else 
            message.english_text for message in messages
        )

    def determine_next_speaking_character(
        self,
        messages: list[Message], 
        characters: list[Character]
    ) -> Character:
        history = self._convert_messages_to_string(reversed(messages), include_character_name=False)
        if len(characters) == 1:
            return characters[0]

        candidate_labels = [character.value for character in characters]
        hypothesis_template = "The next person to speak is {}."

        result = self._onnx_zero_shot_classification(
            self.session, 
            self.tokenizer,
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
            self.session,
            self.tokenizer,
            history,
            poses_descriptions,
            hypothesis_template
        )

        i = poses_descriptions.index(result['labels'][0])
        character_pose = character_poses[i]

        # Get character face
        face_expressions = valid_character_expressions[character_pose]
        face_expressions_descriptions = [face.get_facial_expression_description(face) for face in face_expressions]

        hypothesis_template = f"The {chracter_name} face expression based on response is {{}}"
        
        result = self._onnx_zero_shot_classification(
            self.session,
            self.tokenizer,
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
            self.session,
            self.tokenizer,
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
            self.session,
            self.tokenizer,
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
classifier = Classifier()
