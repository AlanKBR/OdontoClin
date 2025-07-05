"""
Local Transformers Provider - Fallback when vLLM is not available
"""

import logging
from typing import Any, Dict, Optional

from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers.pipelines import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None


class LocalTransformersProvider(BaseAIProvider):
    """
    Local transformers-based AI provider
    Fallback option when vLLM is not available (e.g., Windows)
    """

    def __init__(self, settings: Dict[str, Any]):
        super().__init__(settings)
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.model_name = settings.get("model_name", "microsoft/DialoGPT-small")
        self.device = self._detect_optimal_device(settings)

    def _detect_optimal_device(self, settings: Dict[str, Any]) -> str:
        """Detect optimal device for this system"""
        if not TRANSFORMERS_AVAILABLE or torch is None:
            return "cpu"

        # Check settings first
        provider_settings = settings.get("providers", {}).get("local", {})
        configured_device = provider_settings.get("device", "auto")
        gpu_type = provider_settings.get("gpu_type", "unknown")

        if configured_device != "auto":
            # If CUDA requested but not available, fallback to CPU
            if "cuda" in configured_device and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available, falling back to CPU")
                return "cpu"
            return configured_device

        # Auto-detect optimal device
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            if device_count > 0:
                # Check if it's AMD (ROCm) or NVIDIA
                try:
                    device_name = torch.cuda.get_device_name(0).lower()
                    logger.info(f"Detected GPU: {device_name}")

                    if gpu_type == "amd" or "amd" in device_name or "radeon" in device_name:
                        logger.info("AMD GPU detected - using CUDA API via ROCm")
                        return "cuda:0"  # ROCm uses CUDA API
                    else:
                        logger.info("NVIDIA GPU detected")
                        return "cuda:0"
                except Exception as e:
                    logger.warning(f"GPU detection error: {e}")
                    return "cuda:0"  # Default to first GPU

        # CPU with AMD optimizations
        if gpu_type == "amd":
            logger.info("AMD system detected - using CPU with optimizations")
        else:
            logger.info("No GPU detected - falling back to CPU")
        return "cpu"
        return "cpu"

    def initialize(self) -> bool:
        """Initialize transformers provider"""
        if not TRANSFORMERS_AVAILABLE or torch is None or AutoTokenizer is None or AutoModelForCausalLM is None or pipeline is None:
            logger.error("Transformers dependencies not available")
            return False

        if self.is_initialized:
            return True

        try:
            logger.info("Initializing Local Transformers provider...")
            logger.info(f"Target device: {self.device}")

            cache_dir = self.settings.get("cache_dir", "./models_cache/")

            # Load tokenizer first
            logger.info(f"Loading tokenizer for {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, cache_dir=cache_dir, trust_remote_code=True
            )

            # Configure model loading based on device
            model_kwargs = {"cache_dir": cache_dir, "trust_remote_code": True}

            if "cuda" in self.device and torch.cuda.is_available():
                # GPU configuration
                logger.info(f"Configuring for GPU: {self.device}")
                model_kwargs.update(
                    {
                        "device_map": "auto",
                        "torch_dtype": torch.float16,  # Use FP16 for GPU efficiency
                        "low_cpu_mem_usage": True,
                    }
                )
            else:
                # CPU configuration
                logger.info("Configuring for CPU")
                model_kwargs.update(
                    {
                        "torch_dtype": torch.float32,
                        "device_map": None,
                    }  # Use FP32 for CPU
                )

            # Load model
            logger.info(f"Loading model {self.model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_kwargs)

            # Move to device if needed
            if "cuda" not in str(self.model.device) and "cuda" in self.device:
                logger.info(f"Moving model to {self.device}")
                self.model = self.model.to(self.device)

            # Create pipeline
            pipeline_kwargs = {
                "model": self.model,
                "tokenizer": self.tokenizer,
                "max_new_tokens": self.settings.get("max_tokens", 512),
                "temperature": self.settings.get("temperature", 0.7),
                "do_sample": True,
                "return_full_text": False,
            }

            # Add device to pipeline if GPU
            if "cuda" in self.device:
                pipeline_kwargs["device"] = self.device

            self.pipeline = pipeline("text-generation", **pipeline_kwargs)

            self.is_initialized = True
            logger.info(f"Local Transformers provider initialized successfully on {self.device}")

            # Log GPU memory info if available
            if "cuda" in self.device and torch.cuda.is_available():
                try:
                    memory_allocated = torch.cuda.memory_allocated(self.device) / 1024**3  # GB
                    memory_reserved = torch.cuda.memory_reserved(self.device) / 1024**3  # GB
                    logger.info(
                        f"GPU Memory - Allocated: {memory_allocated:.2f}GB, Reserved: {memory_reserved:.2f}GB"
                    )
                except Exception:
                    pass

            return True

        except Exception as e:
            logger.error(f"Failed to initialize Local Transformers provider: {e}")
            return False

    def is_available(self) -> bool:
        """Check if provider is available"""
        return TRANSFORMERS_AVAILABLE and self.is_initialized

    def generate_response(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generate response using local model"""

        # Validate query
        validation = self.validate_query(query)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"], "response": ""}

        if not self.is_available() or self.pipeline is None or self.tokenizer is None:
            return {
                "success": False,
                "error": "Local Transformers provider not available",
                "response": "",
            }

        try:
            # Prepare prompt
            prompt = self._prepare_prompt(query, context)

            # Generate response using pipeline
            try:
                # Use the pipeline for simpler generation
                generated = self.pipeline(
                    prompt,
                    max_length=len(prompt.split()) + self.settings.get("max_tokens", 150),
                    temperature=self.settings.get("temperature", 0.7),
                    do_sample=True,
                    truncation=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3,
                    top_p=0.9,
                )

                # Extract the generated text
                response_text = generated[0]["generated_text"]

                # Remove the original prompt from the response
                if response_text.startswith(prompt):
                    response_text = response_text[len(prompt) :].strip()

                # Clean up the response
                response_text = self._clean_response(response_text)

                return {
                    "success": True,
                    "response": self.format_response(response_text),
                    "model": self.model_name,
                    "provider": "Local Transformers",
                }
            except Exception as e:
                logger.warning(f"Pipeline generation failed, trying direct model approach: {e}")

                # Check if we have all required components for fallback
                if torch is None or self.model is None or self.tokenizer is None:
                    logger.error("Required components not available for fallback generation")
                    return {"success": False, "error": "Model components not available", "response": ""}

                # Fallback to basic generation
                inputs = self.tokenizer.encode(
                    prompt, return_tensors="pt", truncation=True, max_length=512
                )

                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=inputs.shape[1] + 100,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                    )

                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response_text = generated_text[len(prompt) :].strip()

                return {
                    "success": True,
                    "response": self.format_response(self._clean_response(response_text)),
                    "model": self.model_name,
                    "provider": "Local Transformers",
                }

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"success": False, "error": str(e), "response": ""}

    def _prepare_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Prepare prompt for the AI model"""
        system_prompt = self.settings.get(
            "system_prompt",
            "Você é um assistente especializado em odontologia. Responda de forma clara e precisa.",
        )

        prompt = system_prompt + "\n\n"

        if context:
            prompt += f"Contexto: {context}\n\n"

        prompt += f"Pergunta: {query}\n\nResposta:"

        return prompt

    def _clean_response(self, response: str) -> str:
        """Clean and format the AI response"""
        if not response:
            return "Desculpe, não consegui gerar uma resposta adequada."

        # Remove common artifacts
        response = response.strip()

        # Remove partial sentences at the end
        sentences = response.split(".")
        if len(sentences) > 1 and sentences[-1].strip() and len(sentences[-1].strip()) < 10:
            response = ".".join(sentences[:-1]) + "."

        # Ensure minimum length
        if len(response.strip()) < 20:
            return (
                "Desculpe, não consegui gerar uma resposta completa. Tente reformular sua pergunta."
            )

        return response

    def cleanup(self):
        """Cleanup resources"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if self.pipeline:
            del self.pipeline

        # Clear GPU cache if available
        if TRANSFORMERS_AVAILABLE and torch and torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.is_initialized = False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        info = super().get_provider_info()
        info.update(
            {
                "model_name": self.model_name,
                "transformers_available": TRANSFORMERS_AVAILABLE,
                "device": (
                    "cuda"
                    if (TRANSFORMERS_AVAILABLE and torch and torch.cuda.is_available())
                    else "cpu"
                ),
            }
        )
        return info
