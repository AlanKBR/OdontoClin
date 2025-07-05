"""
AI Assistant Routes - Blueprint for AI functionality
"""

import logging

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.decorators import debug_login_optional
from app.services.ai_assistant import ai_assistant

logger = logging.getLogger(__name__)

# Create blueprint
ai_assistant_bp = Blueprint("ai_assistant", __name__, url_prefix="/ai")

# Initialize model manager (lazy loading)
_model_manager = None


def get_model_manager():
    """Get model manager instance with lazy loading"""
    global _model_manager
    if _model_manager is None:
        from app.services.model_manager import ModelManager

        _model_manager = ModelManager()
    return _model_manager


@ai_assistant_bp.route("/")
@debug_login_optional
def index():
    """Main AI Assistant interface"""
    if not ai_assistant.is_enabled():
        flash("Assistente de IA não está disponível.", "warning")
        return redirect(url_for("main.index"))

    # No auto-initialization - manual control only
    model_info = ai_assistant.get_model_info()
    chat_history = ai_assistant.get_chat_history()

    return render_template(
        "ai_assistant/index.html", model_info=model_info, chat_history=chat_history
    )


@ai_assistant_bp.route("/chat", methods=["POST"])
@debug_login_optional
def chat():
    """Handle chat requests"""
    if not ai_assistant.is_enabled():
        return jsonify({"success": False, "error": "AI Assistant not available"}), 503

    # Try to initialize if not already initialized
    if not ai_assistant.is_initialized:
        try:
            if not ai_assistant.initialize():
                return (
                    jsonify({"success": False, "error": "Failed to initialize AI Assistant"}),
                    503,
                )
        except Exception as e:
            logger.error(f"Failed to initialize AI Assistant during chat: {e}")
            return (
                jsonify({"success": False, "error": f"Initialization error: {str(e)}"}),
                503,
            )

    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        context = data.get("context", "")

        if not query:
            return jsonify({"success": False, "error": "Query is required"}), 400

        # Generate AI response
        result = ai_assistant.generate_response(query, context)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@ai_assistant_bp.route("/status")
@debug_login_optional
def status():
    """Get AI Assistant status"""
    return jsonify(ai_assistant.get_model_info())


@ai_assistant_bp.route("/history")
@debug_login_optional
def history():
    """Get chat history"""
    return jsonify({"history": ai_assistant.get_chat_history()})


@ai_assistant_bp.route("/clear-history", methods=["POST"])
@debug_login_optional
def clear_history():
    """Clear chat history"""
    try:
        ai_assistant.clear_history()
        return jsonify({"success": True, "message": "History cleared"})
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return jsonify({"success": False, "error": "Failed to clear history"}), 500


@ai_assistant_bp.route("/initialize", methods=["POST"])
@debug_login_optional
def initialize():
    """Manually initialize the AI model"""
    try:
        success = ai_assistant.initialize()

        if success:
            return jsonify({"success": True, "message": "AI Assistant initialized successfully"})
        else:
            return (
                jsonify({"success": False, "error": "Failed to initialize AI Assistant"}),
                500,
            )

    except Exception as e:
        logger.error(f"Error initializing AI: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/config")
@debug_login_optional
def config():
    """AI Configuration Panel"""
    if not ai_assistant.is_enabled():
        flash("Assistente de IA não está disponível.", "warning")
        return redirect(url_for("main.index"))

    # Get current configuration and hardware info
    config_data = ai_assistant.get_configuration_data()
    return render_template("ai_assistant/config.html", config_data=config_data)


@ai_assistant_bp.route("/api/hardware-info", methods=["GET"])
@debug_login_optional
def get_hardware_info():
    """Get hardware detection information"""
    try:
        from app.services.hardware_detector import detect_system_capabilities

        hardware_info = detect_system_capabilities()
        return jsonify({"success": True, "hardware": hardware_info})
    except Exception as e:
        logger.error(f"Error detecting hardware: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/available-models", methods=["GET"])
@debug_login_optional
def get_available_models():
    """Get list of available local models"""
    try:
        models = ai_assistant.scan_available_models()
        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"Error scanning models: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/update-config", methods=["POST"])
@debug_login_optional
def update_config():
    """Update AI configuration"""
    try:
        config_data = request.get_json()
        success = ai_assistant.update_configuration(config_data)

        if success:
            return jsonify({"success": True, "message": "Configuration updated successfully"})
        else:
            return (
                jsonify({"success": False, "error": "Failed to update configuration"}),
                500,
            )

    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/stop", methods=["POST"])
@debug_login_optional
def stop_ai():
    """Stop AI Assistant"""
    try:
        ai_assistant.stop()
        return jsonify({"success": True, "message": "AI Assistant stopped"})
    except Exception as e:
        logger.error(f"Error stopping AI: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/status", methods=["GET"])
@debug_login_optional
def get_status():
    """Get current AI status"""
    try:
        status = ai_assistant.get_detailed_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Model Management API Endpoints


@ai_assistant_bp.route("/api/models/search", methods=["GET"])
@debug_login_optional
def search_models():
    """Buscar modelos no Hugging Face"""
    try:
        from app.services.model_manager import ModelManager

        query = request.args.get("query", "")
        filter_type = request.args.get("filter", "all")
        limit = int(request.args.get("limit", 20))

        model_manager = ModelManager()
        models = model_manager.search_huggingface_models(query, filter_type, limit)

        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"Error searching models: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/models/installed", methods=["GET"])
@debug_login_optional
def get_installed_models():
    """Listar modelos instalados"""
    try:
        from app.services.model_manager import ModelManager

        model_manager = ModelManager()
        models = model_manager.get_installed_models()
        disk_usage = model_manager.get_disk_usage()

        return jsonify({"success": True, "models": models, "disk_usage": disk_usage})
    except Exception as e:
        logger.error(f"Error getting installed models: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/models/download", methods=["POST"])
@debug_login_optional
def download_model():
    """Baixar modelo do Hugging Face"""
    try:
        from app.services.model_manager import ModelManager

        data = request.get_json()
        model_name = data.get("model_name")

        if not model_name:
            return (
                jsonify({"success": False, "error": "Nome do modelo é obrigatório"}),
                400,
            )

        model_manager = ModelManager()
        result = model_manager.download_model(model_name)

        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/models/remove", methods=["DELETE"])
@debug_login_optional
def remove_model():
    """Remover modelo instalado"""
    try:
        from app.services.model_manager import ModelManager

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Dados JSON inválidos"}), 400

        model_name = data.get("model_name")

        if not model_name:
            return (
                jsonify({"success": False, "error": "Nome do modelo é obrigatório"}),
                400,
            )

        # Validar nome do modelo
        if not isinstance(model_name, str) or not model_name.strip():
            return jsonify({"success": False, "error": "Nome do modelo inválido"}), 400

        model_manager = ModelManager()
        result = model_manager.remove_model(model_name.strip())

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error removing model: {e}")
        return jsonify({"success": False, "error": f"Erro interno: {str(e)}"}), 500


@ai_assistant_bp.route("/api/models/details/<path:model_name>", methods=["GET"])
@debug_login_optional
def get_model_details(model_name):
    """Obter detalhes de um modelo"""
    try:
        from app.services.model_manager import ModelManager

        model_manager = ModelManager()
        details = model_manager.get_model_details(model_name)

        if "error" not in details:
            return jsonify({"success": True, "model": details})
        else:
            return jsonify({"success": False, "error": details["error"]}), 404

    except Exception as e:
        logger.error(f"Error getting model details: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/models/disk-usage", methods=["GET"])
@debug_login_optional
def get_disk_usage():
    """Obter informações de uso de disco"""
    try:
        from app.services.model_manager import ModelManager

        model_manager = ModelManager()
        usage = model_manager.get_disk_usage()

        if "error" not in usage:
            return jsonify({"success": True, "usage": usage})
        else:
            return jsonify({"success": False, "error": usage["error"]}), 500

    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_assistant_bp.route("/api/models/cleanup", methods=["POST"])
@debug_login_optional
def cleanup_model_cache():
    """Limpar arquivos incompletos e corrompidos"""
    try:
        from app.services.model_manager import ModelManager

        model_manager = ModelManager()
        result = model_manager.cleanup_incomplete_downloads()

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error cleaning up model cache: {e}")
        return jsonify({"success": False, "error": f"Erro interno: {str(e)}"}), 500


@ai_assistant_bp.route("/api/models/<path:model_name>/progress", methods=["GET"])
@debug_login_optional
def get_download_progress(model_name):
    """Obter progresso de download de um modelo"""
    try:
        from app.services.model_manager import ModelManager

        model_manager = ModelManager()
        progress = model_manager.get_download_progress(model_name)

        return jsonify({"success": True, "progress": progress})
    except Exception as e:
        logger.error(f"Error getting download progress: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
