"""
AI Assistant Service - Modular implementation with multiple providers
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    # Import our modular AI providers
    from .ai_providers import BaseAIProvider, ProviderFactory

    AI_PROVIDERS_AVAILABLE = True
except ImportError:
    AI_PROVIDERS_AVAILABLE = False
    ProviderFactory = None
    BaseAIProvider = None

logger = logging.getLogger(__name__)


class AIAssistantService:
    """
    Modular AI Assistant Service with multiple provider support
    Supports vLLM, OpenAI, and other providers with fallback mechanisms
    """

    def __init__(self):
        self.provider = None
        self.settings = self._load_settings()
        self.is_initialized = False
        self.chat_history = []

    def _load_settings(self) -> Dict[str, Any]:
        """Load AI settings from config file"""
        try:
            config_path = os.path.join("config", "ai_settings.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"ai_enabled": False}
        except Exception as e:
            logger.error(f"Error loading AI settings: {e}")
            return {"ai_enabled": False}

    def is_enabled(self) -> bool:
        """Check if AI is enabled and providers are available"""
        return self.settings.get("ai_enabled", False) and AI_PROVIDERS_AVAILABLE

    def initialize(self) -> bool:
        """Initialize the AI assistant with preferred provider"""
        if self.is_initialized or not self.is_enabled():
            return self.is_initialized

        try:
            logger.info("Initializing AI Assistant...")

            # Get provider preference from settings
            provider_config = self.settings.get("providers", {})
            preferred_providers = provider_config.get("preferred_order", ["vllm", "openai"])

            # Create provider with fallback
            if ProviderFactory:
                self.provider = ProviderFactory.create_with_fallback(
                    preferred_providers, self.settings
                )
            else:
                logger.error("ProviderFactory not available")
                return False

            if self.provider:
                self.is_initialized = True
                logger.info(f"AI Assistant initialized with {self.provider.__class__.__name__}")
                return True
            else:
                logger.error("Failed to initialize any AI provider")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize AI Assistant: {e}")
            self.is_initialized = False
            return False

    def generate_response(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI response using the active provider

        Args:
            query: User's question/input
            context: Optional context from the application

        Returns:
            Dictionary with response, success status, and metadata
        """
        if not self.is_enabled():
            return {
                "success": False,
                "error": "AI Assistant is disabled or providers not available",
                "response": "",
            }

        if not self.is_initialized and not self.initialize():
            return {
                "success": False,
                "error": "Failed to initialize AI provider",
                "response": "",
            }

        if not self.provider:
            return {
                "success": False,
                "error": "No AI provider available",
                "response": "",
            }

        try:
            # Generate response using the active provider
            result = self.provider.generate_response(query, context)

            # Store in chat history if enabled and successful
            if result.get("success") and self.settings.get("ui_settings", {}).get(
                "enable_chat_history", True
            ):
                self._add_to_history(query, result.get("response", ""))

            return result

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {"success": False, "error": str(e), "response": ""}

    def _prepare_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Prepare the prompt for the AI model - delegated to provider"""
        # This method is now handled by individual providers
        # Kept for backwards compatibility
        return query

    def _add_to_history(self, query: str, response: str):
        """Add interaction to chat history"""
        max_items = self.settings.get("ui_settings", {}).get("max_history_items", 50)

        self.chat_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
            }
        )

        # Keep only the most recent items
        if len(self.chat_history) > max_items:
            self.chat_history = self.chat_history[-max_items:]

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get recent chat history"""
        return self.chat_history

    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current AI setup"""
        if not self.is_enabled():
            return {
                "enabled": False,
                "initialized": False,
                "dependencies_available": AI_PROVIDERS_AVAILABLE,
                "model_name": "N/A",
            }

        info = {
            "enabled": True,
            "initialized": self.is_initialized,
            "dependencies_available": AI_PROVIDERS_AVAILABLE,
            "providers_available": AI_PROVIDERS_AVAILABLE,
            "settings": self.settings,
            "model_name": "Não inicializado",
        }

        if self.provider:
            provider_info = self.provider.get_provider_info()
            info["active_provider"] = provider_info
            info["model_name"] = provider_info.get("model", "Modelo desconhecido")

        return info

    def switch_provider(self, provider_type: str) -> bool:
        """Switch to a different provider"""
        if not self.is_enabled():
            return False

        try:
            if ProviderFactory:
                new_provider = ProviderFactory.create_provider(provider_type, self.settings)
            else:
                return False

            if new_provider and new_provider.initialize():
                # Cleanup old provider
                if self.provider and hasattr(self.provider, "cleanup"):
                    self.provider.cleanup()

                self.provider = new_provider
                logger.info(f"Switched to {provider_type} provider")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to switch provider: {e}")
            return False

    def cleanup(self):
        """Cleanup AI assistant resources"""
        if self.provider:
            if hasattr(self.provider, "cleanup"):
                self.provider.cleanup()
        self.provider = None
        self.is_initialized = False

    def get_configuration_data(self) -> Dict[str, Any]:
        """Get current configuration and available options"""
        return {
            "current_settings": self.settings,
            "is_initialized": self.is_initialized,
            "providers": (list(ProviderFactory.PROVIDERS.keys()) if ProviderFactory else []),
            "current_provider": (self.provider.__class__.__name__ if self.provider else None),
        }

    def scan_available_models(self) -> List[Dict[str, Any]]:
        """Scan for available local models"""
        models = []
        models_dir = (
            self.settings.get("providers", {}).get("local", {}).get("cache_dir", "./models_cache/")
        )

        try:
            import os

            if os.path.exists(models_dir):
                for item in os.listdir(models_dir):
                    model_path = os.path.join(models_dir, item)
                    if os.path.isdir(model_path):
                        # Basic model info - could be expanded with metadata
                        models.append(
                            {
                                "name": item,
                                "path": model_path,
                                "type": "local",
                                "size": self._get_dir_size(model_path),
                            }
                        )
        except Exception as e:
            logger.error(f"Error scanning models: {e}")

        return models

    def _get_dir_size(self, path: str) -> str:
        """Get directory size in human readable format"""
        try:
            import os

            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)

            # Convert to human readable
            for unit in ["B", "KB", "MB", "GB"]:
                if total_size < 1024.0:
                    return f"{total_size:.1f} {unit}"
                total_size /= 1024.0
            return f"{total_size:.1f} TB"
        except Exception:
            return "Unknown"

    def update_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Update AI configuration"""
        try:
            # Update settings
            self.settings.update(config_data)

            # Save to file
            config_path = os.path.join("config", "ai_settings.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)

            # If currently initialized and provider changed, reinitialize
            if self.is_initialized and config_data.get("provider_change"):
                self.stop()
                return self.initialize()

            return True
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False

    def stop(self):
        """Stop AI assistant and cleanup resources"""
        try:
            if self.provider and hasattr(self.provider, "cleanup"):
                self.provider.cleanup()
            self.provider = None
            self.is_initialized = False
            logger.info("AI Assistant stopped")
        except Exception as e:
            logger.error(f"Error stopping AI Assistant: {e}")

    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        status = {
            "enabled": self.is_enabled(),
            "initialized": self.is_initialized,
            "provider_available": AI_PROVIDERS_AVAILABLE,
            "current_provider": None,
            "provider_info": None,
            "hardware_status": None,
            "model_status": None,
        }

        if self.provider:
            try:
                provider_info = self.provider.get_provider_info()
                status["current_provider"] = provider_info.get("provider_type")
                status["provider_info"] = provider_info
            except Exception as e:
                logger.error(f"Error getting provider info: {e}")

        return status


# Global instance - singleton pattern for efficiency
ai_assistant = AIAssistantService()
