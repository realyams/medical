import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# Global state for lazy-loading the model
_model = None
_processor = None
_is_loaded = False

def load_model():
    """
    Loads the LLaVA model and the medical LoRA adapter.
    """
    global _model, _processor, _is_loaded
    if _is_loaded:
        return

    try:
        import torch
        from transformers import AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig
        from peft import PeftModel
        import os

        # Model used in the training notebook
        model_id = "llava-hf/llava-1.5-7b-hf"
        # The path where the adapter was saved
        adapter_path = "./medical_llava_weights" 

        # 1. Define Quantization Config (4-bit to save memory)
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )

        logger.info("Loading processor...")
        _processor = AutoProcessor.from_pretrained(model_id)

        logger.info("Loading base LLaVA model in 4-bit...")
        base_model = LlavaForConditionalGeneration.from_pretrained(
            model_id, 
            quantization_config=quant_config,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True
        )

        # 2. Try to load the medical adapter if it exists
        if os.path.exists(adapter_path):
            logger.info(f"Loading medical LoRA adapter from {adapter_path}...")
            _model = PeftModel.from_pretrained(base_model, adapter_path)
        else:
            logger.warning(f"Adapter not found at {adapter_path}. Using base model.")
            _model = base_model

        _is_loaded = True
        logger.info("AI Model loaded successfully.")
    except ImportError as e:
        logger.error(f"Missing required ML libraries: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load AI model: {e}")
        raise

def analyze_medical_data(context: str, image_bytes: bytes = None):
    """
    Runs the multimodal inference.
    """
    global _model, _processor, _is_loaded
    
    if not _is_loaded:
        try:
            load_model()
        except Exception as e:
            return {"error": "Model failed to load. Are torch/transformers installed?", "details": str(e)}

    import torch
    
    try:
        # If an image was provided, use it. Otherwise create a blank placeholder
        if image_bytes:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        else:
            image = Image.new('RGB', (224, 224), color=(0, 0, 0))
            
        prompt = f"USER: <image>\nAnalyze this medical case and describe the clinical observations. Context: {context}\nASSISTANT:"

        device = "cuda" if torch.cuda.is_available() else "cpu"
        inputs = _processor(text=prompt, images=image, return_tensors="pt").to(device)
        
        logger.info("Running AI model inference...")
        with torch.no_grad():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2
            )
            
        # Decode only the generated part
        input_length = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0, input_length:]
        response_text = _processor.decode(generated_tokens, skip_special_tokens=True).strip()
        
        return {
            "analysis": response_text
        }

    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return {"error": "Inference failed", "details": str(e)}
