import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from onnxruntime.quantization import quantize_dynamic, QuantType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_nli_model_to_onnx(model_name: str, output_path: str, quantized_path: str):
    """
    Convert a NLI model to ONNX and then quantize it
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        logger.info(f"Loading NLI model: {model_name}")
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
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
        
        # Extract input names and create dynamic axes
        input_names = list(inputs.keys())
        dynamic_axes = {
            name: {0: "batch_size", 1: "sequence_length"} 
            for name in input_names
        }
        dynamic_axes["logits"] = {0: "batch_size"}
        
        logger.info(f"Exporting NLI model to ONNX: {output_path}")
        
        # Export to ONNX with higher opset version for better compatibility
        with torch.no_grad():
            torch.onnx.export(
                model,
                tuple(inputs.values()),
                output_path,
                input_names=input_names,
                output_names=["logits"],
                dynamic_axes=dynamic_axes,
                do_constant_folding=True,
                opset_version=14,  # Higher opset version for better DeBERTa support
                export_params=True,
                verbose=False
            )
        
        logger.info(f"Quantizing model: {quantized_path}")
        
        # Try quantization with more conservative settings
        try:
            quantize_dynamic(
                output_path,
                quantized_path,
                weight_type=QuantType.QUInt8,  # Try unsigned int8 first
                optimize_model=False,  # Disable optimization to avoid type issues
                per_channel=False,  # Disable per-channel quantization
                reduce_range=True,  # Enable reduce range for better compatibility
                activation_type=QuantType.QUInt8,
                extra_options={'WeightSymmetric': False}
            )
        except Exception as e:
            logger.warning(f"QUInt8 quantization failed: {e}")
            logger.info("Trying QInt8 quantization...")
            try:
                quantize_dynamic(
                    output_path,
                    quantized_path,
                    weight_type=QuantType.QInt8,
                    optimize_model=False,
                    per_channel=False,
                    reduce_range=True
                )
            except Exception as e2:
                logger.error(f"QInt8 quantization also failed: {e2}")
                logger.info("Copying original ONNX model without quantization...")
                import shutil
                shutil.copy2(output_path, quantized_path)

    except Exception as e:
        logger.error(f"Failed to convert {model_name}: {e}")
        raise

def main():
    """
    Convert both models used in the classifier
    """
    # Use absolute path to ensure models are created in the right location
    models_dir = "/app/models"
    
    # Create the directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    # Model configurations
    models_to_convert = [
        {
            "name": "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33",
            "output": f"{models_dir}/speaker_model.onnx",
            "quantized": f"{models_dir}/speaker_model_quantized.onnx"
        },
        {
            "name": "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33",
            "output": f"{models_dir}/sprite_model.onnx", 
            "quantized": f"{models_dir}/sprite_model_quantized.onnx"
        }
    ]

    for model_config in models_to_convert:
        convert_nli_model_to_onnx(
            model_config["name"],
            model_config["output"],
            model_config["quantized"]
        )

if __name__ == "__main__":
    main() 