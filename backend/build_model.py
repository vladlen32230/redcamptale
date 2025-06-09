#!/usr/bin/env python3
"""
Script to download and convert model to ONNX during Docker build
"""
import os
import torch
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_onnx_model():
    # Model name from environment variable
    model_name = os.environ["STANDARD_CLASSIFIER_NAME"]
    
    logger.info(f"Loading model from transformers: {model_name}")
    
    # Load tokenizer and model from transformers
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # Set model to evaluation mode
    model.eval()
    
    # Create dummy inputs for export (premise-hypothesis pair)
    premise = "This is a sample premise text for ONNX export."
    hypothesis = "This is about exporting models."

    inputs = tokenizer(
        premise,
        hypothesis,
        return_tensors="pt",
        max_length=512,
        padding="max_length",
        truncation=True
    )
    
    logger.info("Converting model to ONNX format...")
    
    # Create models directory
    models_dir = "/models"
    os.makedirs(models_dir, exist_ok=True)
    
    # ONNX model path
    onnx_model_path = os.path.join(models_dir, "classifier.onnx")
    
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
            onnx_model_path,
            input_names=input_names,
            output_names=["logits"],
            dynamic_axes=dynamic_axes,
            do_constant_folding=True,
            opset_version=14,  # Higher opset version for better DeBERTa support
            export_params=True,
            verbose=False
        )
    
    logger.info(f"Model converted to ONNX and saved to: {onnx_model_path}")

    # Save tokenizer to the models directory
    tokenizer_path = os.path.join(models_dir, "tokenizer")
    tokenizer.save_pretrained(tokenizer_path)
    logger.info(f"Tokenizer saved to: {tokenizer_path}")
    
    logger.info("Model building completed successfully!")

if __name__ == "__main__":
    build_onnx_model() 