"""
Model Manager Service
Gerencia download, remoção e busca de modelos do Hugging Face
"""

import gc
import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

try:
    from huggingface_hub import HfApi, hf_hub_download, model_info, snapshot_download
    from huggingface_hub.errors import RepositoryNotFoundError, RevisionNotFoundError

    HUGGINGFACE_HUB_AVAILABLE = True
except ImportError:
    HUGGINGFACE_HUB_AVAILABLE = False
    HfApi = None
    hf_hub_download = None
    model_info = None
    snapshot_download = None
    RepositoryNotFoundError = Exception
    RevisionNotFoundError = Exception


class ModelManager:
    """
    Gerenciador de modelos de linguagem com integração ao Hugging Face
    """

    def __init__(self, cache_dir: str = "./models_cache/"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if HUGGINGFACE_HUB_AVAILABLE and HfApi is not None:
            self.api = HfApi()
        else:
            self.api = None

        # Sistema de progresso de download
        self.download_progress = {}

        # Filtros de modelos recomendados para aplicações médicas/odontológicas
        self.medical_keywords = [
            "medical",
            "bio",
            "clinical",
            "health",
            "medicina",
            "odonto",
            "dental",
            "saude",
            "clinica",
            "biomedical",
            "biomed",
        ]

        # Modelos populares e compatíveis
        self.recommended_models = [
            "microsoft/DialoGPT-small",
            "microsoft/DialoGPT-medium",
            "pierreguillou/gpt2-small-portuguese",
            "neuralmind/bert-base-portuguese-cased",
            "BioMistral/BioMistral-7B",
            "BioMistral/BioMistral-7B-AWQ-QGS128-W4-GEMV",
            "microsoft/BioGPT-Large",
            "allenai/scibert_scivocab_uncased",
        ]

    def is_available(self) -> bool:
        """Verifica se o gerenciador está disponível"""
        return HUGGINGFACE_HUB_AVAILABLE and REQUESTS_AVAILABLE

    def get_installed_models(self) -> List[Dict[str, Any]]:
        """Obtém lista de modelos instalados localmente"""
        models = []

        try:
            for item in self.cache_dir.iterdir():
                if item.is_dir() and item.name.startswith("models--"):
                    model_info = self._analyze_local_model(item)
                    if model_info:
                        models.append(model_info)
        except Exception as e:
            logger.error(f"Erro ao listar modelos instalados: {e}")

        return sorted(models, key=lambda x: x.get("name", ""))

    def _analyze_local_model(self, model_path: Path) -> Optional[Dict[str, Any]]:
        """Analisa um modelo local e extrai informações"""
        try:
            # Converter nome da pasta para nome do modelo
            model_name = model_path.name.replace("models--", "").replace("--", "/")

            # Calcular tamanho
            total_size = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
            size_mb = round(total_size / (1024 * 1024), 1)
            size_gb = round(total_size / (1024 * 1024 * 1024), 2)

            # Tentar ler configuração do modelo
            config_info = self._read_model_config(model_path)

            # Determinar tipo baseado no nome e configuração
            model_type = self._determine_model_type(model_name, config_info)

            return {
                "name": model_name,
                "display_name": model_name.split("/")[-1],
                "organization": (model_name.split("/")[0] if "/" in model_name else "local"),
                "path": str(model_path),
                "size_mb": size_mb,
                "size_gb": size_gb,
                "size_display": f"{size_gb} GB" if size_gb >= 1 else f"{size_mb} MB",
                "type": model_type,
                "config": config_info,
                "installed": True,
                "can_remove": True,
            }
        except Exception as e:
            logger.error(f"Erro ao analisar modelo {model_path}: {e}")
            return None

    def _read_model_config(self, model_path: Path) -> Dict[str, Any]:
        """Lê configuração de um modelo local"""
        config = {}

        try:
            # Procurar config.json nos snapshots
            for config_file in model_path.rglob("config.json"):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    break
        except Exception as e:
            logger.error(f"Não foi possível ler config de {model_path}: {e}")

        return config

    def _determine_model_type(self, model_name: str, config: Dict[str, Any]) -> str:
        """Determina o tipo do modelo baseado no nome e configuração"""
        name_lower = model_name.lower()

        # Verificar palavras-chave médicas
        if any(keyword in name_lower for keyword in self.medical_keywords):
            return "medical"

        # Verificar por arquitetura
        architectures = config.get("architectures", [])
        if architectures:
            arch = architectures[0].lower()
            if "gpt" in arch or "causal" in arch:
                return "conversational"
            elif "bert" in arch:
                return "language_model"

        # Verificar por nome específico
        if "dialog" in name_lower or "chat" in name_lower:
            return "conversational"
        elif "bert" in name_lower:
            return "language_model"
        elif "gpt" in name_lower:
            return "conversational"

        return "general"

    def search_huggingface_models(
        self, query: str = "", filter_type: str = "all", limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Busca modelos no Hugging Face Hub"""
        if not self.is_available():
            logger.warning("ModelManager not available for HF search")
            return []

        try:
            models = []

            # Se não há query, usar modelos recomendados
            if not query.strip():
                logger.info("No query provided, returning recommended models")
                models.extend(self._get_recommended_models())
            else:
                logger.info(f"Searching HF Hub for: '{query}' with filter: '{filter_type}'")

                if not self.api:
                    logger.error("HuggingFace Hub not available")
                    return []

                # Buscar no HF Hub
                search_results = self.api.list_models(
                    search=query,
                    limit=limit,
                    sort="downloads",
                    direction=-1,
                    library="transformers",
                )

                logger.info(f"HF Hub returned {len(list(search_results))} initial results")

                # Reset iterator since we consumed it for counting
                search_results = self.api.list_models(
                    search=query,
                    limit=limit,
                    sort="downloads",
                    direction=-1,
                    library="transformers",
                )

                for model in search_results:
                    model_info = self._format_huggingface_model(model)
                    if model_info:
                        if self._filter_model(model_info, filter_type):
                            models.append(model_info)

                logger.info(f"Final models after processing: {len(models)}")

            return models[:limit]

        except Exception as e:
            logger.error(f"Erro ao buscar modelos no HF: {e}")
            return []

    def _get_recommended_models(self) -> List[Dict[str, Any]]:
        """Retorna modelos recomendados com informações básicas"""
        models = []

        for model_name in self.recommended_models:
            try:
                # Verificar se já está instalado
                installed = self._is_model_installed(model_name)

                models.append(
                    {
                        "name": model_name,
                        "display_name": model_name.split("/")[-1],
                        "organization": model_name.split("/")[0],
                        "description": f"Modelo recomendado: {model_name}",
                        "type": "recommended",
                        "installed": installed,
                        "can_download": not installed,
                        "downloads": "N/A",
                        "size_estimate": "Varia",
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao processar modelo recomendado {model_name}: {e}")

        return models

    def _format_huggingface_model(self, model) -> Optional[Dict[str, Any]]:
        """Formata informações de um modelo do HF Hub"""
        try:
            model_name = model.id  # Corrigido: usar model.id em vez de model.modelId
            installed = self._is_model_installed(model_name)

            # Extrair descrição de forma segura
            description = model_name
            if hasattr(model, "card_data") and model.card_data:
                description = model.card_data.get("title", model_name)

            # Obter tamanho do modelo
            size_info = self._get_model_size(model_name)

            return {
                "name": model_name,
                "display_name": model_name.split("/")[-1],
                "organization": model_name.split("/")[0] if "/" in model_name else "",
                "description": description,
                "type": self._classify_model_type(model_name),
                "installed": installed,
                "can_download": not installed,
                "downloads": getattr(model, "downloads", 0),
                "size_estimate": size_info["formatted"],
                "size_bytes": size_info["bytes"],
                "last_modified": getattr(model, "last_modified", None),
            }
        except Exception as e:
            logger.error(f"Erro ao formatar modelo {model}: {e}")
            return None

    def _classify_model_type(self, model_name: str) -> str:
        """Classifica tipo do modelo baseado no nome"""
        name_lower = model_name.lower()

        if any(keyword in name_lower for keyword in self.medical_keywords):
            return "medical"
        elif "dialog" in name_lower or "chat" in name_lower:
            return "conversational"
        elif "bert" in name_lower:
            return "language_model"
        elif "gpt" in name_lower:
            return "conversational"
        else:
            return "general"

    def _filter_model(self, model_info: Dict[str, Any], filter_type: str) -> bool:
        """Filtra modelos baseado no tipo"""
        if filter_type == "all":
            return True
        return model_info.get("type") == filter_type

    def _is_model_installed(self, model_name: str) -> bool:
        """Verifica se um modelo está instalado"""
        model_path = self.cache_dir / f"models--{model_name.replace('/', '--')}"
        return model_path.exists()

    def download_model(self, model_name: str, progress_callback=None) -> Dict[str, Any]:
        """Baixa um modelo do Hugging Face com progresso"""
        if not self.is_available():
            return {"success": False, "error": "Hugging Face Hub não disponível"}

        if self._is_model_installed(model_name):
            return {"success": False, "error": "Modelo já está instalado"}

        try:
            logger.info(f"Iniciando download do modelo: {model_name}")

            # Verificar espaço em disco
            disk_space = self._get_available_disk_space()
            if disk_space < 1024 * 1024 * 1024:  # 1GB mínimo
                return {
                    "success": False,
                    "error": "Espaço em disco insuficiente (mínimo 1GB)",
                }

            # Inicializar progresso
            self._update_download_progress(model_name, 0, "Iniciando download...")

            # Callback de progresso
            if progress_callback:
                progress_callback(0, "Iniciando download...")

            # Download com progresso customizado
            try:
                local_path = self._download_with_progress(model_name)

                self._update_download_progress(model_name, 100, "Download concluído!")
                if progress_callback:
                    progress_callback(100, "Download concluído!")

                logger.info(f"Modelo {model_name} baixado com sucesso em {local_path}")

                # Limpar progresso após sucesso
                self._clear_download_progress(model_name)

                return {
                    "success": True,
                    "message": f"Modelo {model_name} baixado com sucesso",
                    "path": local_path,
                }

            except Exception as download_error:
                self._clear_download_progress(model_name)
                raise download_error

        except RepositoryNotFoundError:
            self._clear_download_progress(model_name)
            return {
                "success": False,
                "error": f"Modelo {model_name} não encontrado no Hugging Face",
            }
        except RevisionNotFoundError:
            self._clear_download_progress(model_name)
            return {
                "success": False,
                "error": f"Versão do modelo {model_name} não encontrada",
            }
        except Exception as e:
            self._clear_download_progress(model_name)
            logger.error(f"Erro ao baixar modelo {model_name}: {e}")
            return {"success": False, "error": f"Erro no download: {str(e)}"}

    def _download_with_progress(self, model_name: str) -> str:
        """Download com monitoramento de progresso"""
        if not snapshot_download:
            raise RuntimeError("HuggingFace Hub not available")

        # Download usando snapshot_download
        local_path = snapshot_download(
            repo_id=model_name,
            cache_dir=str(self.cache_dir),
            local_files_only=False,
            resume_download=True,
        )

        return local_path

    def remove_model(self, model_name: str) -> Dict[str, Any]:
        """Remove um modelo instalado"""
        try:
            logger.info(f"Iniciando remoção do modelo: {model_name}")

            model_path = self.cache_dir / f"models--{model_name.replace('/', '--')}"

            if not model_path.exists():
                logger.warning(f"Modelo {model_name} não encontrado em {model_path}")
                return {"success": False, "error": "Modelo não está instalado"}

            # Calcular espaço que será liberado
            size_bytes = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
            size_mb = round(size_bytes / (1024 * 1024), 1)

            # Tentar remover com várias estratégias
            success = self._remove_model_directory(model_path)

            if success:
                logger.info(f"Modelo {model_name} removido. Espaço liberado: {size_mb} MB")
                return {
                    "success": True,
                    "message": f"Modelo {model_name} removido com sucesso",
                    "space_freed": f"{size_mb} MB",
                }
            else:
                return {
                    "success": False,
                    "error": "Não foi possível remover completamente o modelo. Alguns arquivos podem estar em uso por outro processo.",
                }

        except Exception as e:
            logger.error(f"Erro ao remover modelo {model_name}: {e}")
            return {"success": False, "error": f"Erro ao remover: {str(e)}"}

    def get_model_details(self, model_name: str) -> Dict[str, Any]:
        """Obtém detalhes completos de um modelo"""
        try:
            # Verificar se está instalado localmente
            if self._is_model_installed(model_name):
                model_path = self.cache_dir / f"models--{model_name.replace('/', '--')}"
                local_info = self._analyze_local_model(model_path)
                if local_info:
                    local_info["source"] = "local"
                    return local_info

            # Buscar informações no HF Hub
            if self.is_available() and model_info is not None:
                info = model_info(model_name)
                return {
                    "name": model_name,
                    "display_name": model_name.split("/")[-1],
                    "organization": model_name.split("/")[0],
                    "description": (
                        getattr(info, "cardData", {}).get("title", model_name)
                        if hasattr(info, "cardData")
                        else model_name
                    ),
                    "type": self._classify_model_type(model_name),
                    "downloads": getattr(info, "downloads", 0),
                    "last_modified": getattr(info, "lastModified", None),
                    "installed": False,
                    "source": "huggingface",
                }

            return {"error": "Modelo não encontrado"}

        except Exception as e:
            logger.error(f"Erro ao obter detalhes do modelo {model_name}: {e}")
            return {"error": str(e)}

    def get_disk_usage(self) -> Dict[str, Any]:
        """Obtém informações de uso de disco"""
        try:
            total_size = sum(f.stat().st_size for f in self.cache_dir.rglob("*") if f.is_file())
            model_count = len(
                [
                    d
                    for d in self.cache_dir.iterdir()
                    if d.is_dir() and d.name.startswith("models--")
                ]
            )
            available_space = self._get_available_disk_space()

            return {
                "cache_dir": str(self.cache_dir),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 1),
                "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
                "model_count": model_count,
                "available_space_bytes": available_space,
                "available_space_gb": round(available_space / (1024 * 1024 * 1024), 1),
            }
        except Exception as e:
            logger.error(f"Erro ao obter uso de disco: {e}")
            return {"error": str(e)}

    def _get_available_disk_space(self) -> int:
        """Obtém espaço disponível em disco"""
        try:
            if os.name == "nt":  # Windows
                import ctypes

                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(str(self.cache_dir)),
                    ctypes.pointer(free_bytes),
                    None,
                    None,
                )
                return free_bytes.value
            else:  # Unix/Linux
                statvfs = os.statvfs(str(self.cache_dir))
                return statvfs.f_frsize * statvfs.f_bavail
        except Exception:
            return 0

    def cleanup_cache(self) -> Dict[str, Any]:
        """Limpa arquivos temporários e locks"""
        try:
            cleaned_files = 0
            cleaned_size = 0

            # Limpar pasta .locks
            locks_dir = self.cache_dir / ".locks"
            if locks_dir.exists():
                for lock_file in locks_dir.rglob("*"):
                    if lock_file.is_file():
                        cleaned_size += lock_file.stat().st_size
                        lock_file.unlink()
                        cleaned_files += 1

            return {
                "success": True,
                "cleaned_files": cleaned_files,
                "cleaned_size_mb": round(cleaned_size / (1024 * 1024), 2),
            }

        except Exception as e:
            logger.error(f"Erro na limpeza de cache: {e}")
            return {"success": False, "error": str(e)}

    def cleanup_incomplete_downloads(self) -> Dict[str, Any]:
        """Remove arquivos incompletos ou corrompidos de downloads"""
        try:
            cleaned_files = []
            cleaned_size = 0

            for model_dir in self.cache_dir.glob("models--*"):
                if model_dir.is_dir():
                    # Procurar arquivos .incomplete
                    for incomplete_file in model_dir.rglob("*.incomplete"):
                        try:
                            size = incomplete_file.stat().st_size
                            incomplete_file.unlink()
                            cleaned_files.append(incomplete_file.name)
                            cleaned_size += size
                            logger.info(f"Arquivo incompleto removido: {incomplete_file}")
                        except Exception as e:
                            logger.warning(f"Não foi possível remover {incomplete_file}: {e}")

                    # Procurar arquivos .lock
                    for lock_file in model_dir.rglob("*.lock"):
                        try:
                            if lock_file.exists():
                                lock_file.unlink()
                                cleaned_files.append(lock_file.name)
                                logger.info(f"Arquivo de lock removido: {lock_file}")
                        except Exception as e:
                            logger.warning(f"Não foi possível remover lock {lock_file}: {e}")

            size_mb = round(cleaned_size / (1024 * 1024), 1)

            return {
                "success": True,
                "cleaned_files": len(cleaned_files),
                "space_freed": f"{size_mb} MB",
                "message": f"Limpeza concluída: {len(cleaned_files)} arquivos removidos",
            }

        except Exception as e:
            logger.error(f"Erro na limpeza de arquivos incompletos: {e}")
            return {"success": False, "error": str(e)}

    def _remove_model_directory(self, model_path: Path) -> bool:
        """Remove diretório do modelo com várias estratégias"""
        try:
            # Primeira tentativa: remoção simples
            logger.info(f"Tentativa 1: Removendo diretório {model_path}")
            shutil.rmtree(model_path)
            return True
        except OSError as e:
            logger.warning(f"Tentativa 1 falhou: {e}")

        try:
            # Segunda tentativa: aguardar e tentar novamente
            logger.info("Tentativa 2: Aguardando 2 segundos e tentando novamente")
            time.sleep(2)
            gc.collect()  # Forçar garbage collection
            shutil.rmtree(model_path)
            return True
        except OSError as e:
            logger.warning(f"Tentativa 2 falhou: {e}")

        try:
            # Terceira tentativa: remover arquivos individualmente
            logger.info("Tentativa 3: Removendo arquivos individualmente")
            removed_count = 0
            total_count = 0

            for root, dirs, files in os.walk(model_path, topdown=False):
                for file in files:
                    total_count += 1
                    file_path = os.path.join(root, file)
                    try:
                        # Tentar remover atributo readonly se houver
                        os.chmod(file_path, 0o777)
                        os.remove(file_path)
                        removed_count += 1
                    except OSError as file_error:
                        logger.warning(
                            f"Não foi possível remover arquivo {file_path}: {file_error}"
                        )

                # Tentar remover diretórios vazios
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                    except OSError:
                        pass

            # Tentar remover o diretório principal
            try:
                os.rmdir(model_path)
                logger.info(
                    f"Remoção parcial concluída: {removed_count}/{total_count} arquivos removidos"
                )
                return removed_count > 0
            except OSError:
                logger.info(
                    f"Remoção parcial concluída: {removed_count}/{total_count} arquivos removidos, diretório principal não pôde ser removido"
                )
                return removed_count > 0

        except Exception as e:
            logger.error(f"Tentativa 3 falhou: {e}")

        # Quarta tentativa: usar comando del do Windows
        try:
            if os.name == "nt":  # Windows
                logger.info("Tentativa 4: Usando comando do sistema para remoção forçada")
                import subprocess

                result = subprocess.run(
                    ["rmdir", "/s", "/q", str(model_path)],
                    capture_output=True,
                    text=True,
                    shell=True,
                )
                if result.returncode == 0:
                    return True
                else:
                    logger.warning(f"Comando rmdir falhou: {result.stderr}")
        except Exception as e:
            logger.warning(f"Tentativa 4 falhou: {e}")

        return False

    def _get_model_size(self, model_name: str) -> Dict[str, Any]:
        """Obtém o tamanho do modelo do HF Hub"""
        try:
            if not self.is_available() or not model_info:
                return {"formatted": "Desconhecido", "bytes": 0}

            # Tentar obter informações do modelo
            info = model_info(model_name)

            if hasattr(info, "siblings") and info.siblings:
                total_size = 0
                for sibling in info.siblings:
                    if hasattr(sibling, "size") and sibling.size:
                        total_size += sibling.size

                if total_size > 0:
                    return {
                        "bytes": total_size,
                        "formatted": self._format_size(total_size),
                    }

            # Fallback: estimar baseado no nome do modelo
            return self._estimate_model_size(model_name)

        except Exception as e:
            logger.warning(f"Erro ao obter tamanho do modelo {model_name}: {e}")
            return {"formatted": "Desconhecido", "bytes": 0}

    def _format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes para formato legível"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def _estimate_model_size(self, model_name: str) -> Dict[str, Any]:
        """Estima o tamanho do modelo baseado no nome"""
        name_lower = model_name.lower()

        # Estimativas baseadas em modelos conhecidos
        if "gpt2" in name_lower:
            if "medium" in name_lower:
                return {"bytes": 1400000000, "formatted": "1.4 GB"}  # ~1.4GB
            elif "large" in name_lower:
                return {"bytes": 3200000000, "formatted": "3.2 GB"}  # ~3.2GB
            elif "xl" in name_lower:
                return {"bytes": 6400000000, "formatted": "6.4 GB"}  # ~6.4GB
            else:
                return {"bytes": 500000000, "formatted": "500 MB"}  # ~500MB (base)

        elif "bert" in name_lower:
            if "large" in name_lower:
                return {"bytes": 1300000000, "formatted": "1.3 GB"}  # ~1.3GB
            else:
                return {"bytes": 400000000, "formatted": "400 MB"}  # ~400MB (base)

        elif "t5" in name_lower:
            if "small" in name_lower:
                return {"bytes": 240000000, "formatted": "240 MB"}  # ~240MB
            elif "base" in name_lower:
                return {"bytes": 850000000, "formatted": "850 MB"}  # ~850MB
            elif "large" in name_lower:
                return {"bytes": 3000000000, "formatted": "3.0 GB"}  # ~3GB
            elif "3b" in name_lower:
                return {"bytes": 11000000000, "formatted": "11 GB"}  # ~11GB
            elif "11b" in name_lower:
                return {"bytes": 42000000000, "formatted": "42 GB"}  # ~42GB

        elif "7b" in name_lower:
            return {"bytes": 14000000000, "formatted": "14 GB"}  # ~14GB
        elif "13b" in name_lower:
            return {"bytes": 26000000000, "formatted": "26 GB"}  # ~26GB
        elif "30b" in name_lower:
            return {"bytes": 60000000000, "formatted": "60 GB"}  # ~60GB
        elif "70b" in name_lower:
            return {"bytes": 140000000000, "formatted": "140 GB"}  # ~140GB

        # Padrão para modelos desconhecidos
        return {"bytes": 1000000000, "formatted": "~1 GB"}

    def get_download_progress(self, model_name: str) -> Dict[str, Any]:
        """Obtém o progresso atual do download de um modelo"""
        progress = self.download_progress.get(model_name, {})
        return {
            "downloading": progress.get("downloading", False),
            "progress": progress.get("progress", 0),
            "status": progress.get("status", ""),
            "downloaded_bytes": progress.get("downloaded_bytes", 0),
            "total_bytes": progress.get("total_bytes", 0),
            "speed": progress.get("speed", 0),
            "eta": progress.get("eta", 0),
        }

    def _update_download_progress(
        self,
        model_name: str,
        progress: int,
        status: str,
        downloaded: int = 0,
        total: int = 0,
        speed: float = 0,
        eta: int = 0,
    ):
        """Atualiza o progresso do download"""
        self.download_progress[model_name] = {
            "downloading": progress < 100,
            "progress": progress,
            "status": status,
            "downloaded_bytes": downloaded,
            "total_bytes": total,
            "speed": speed,
            "eta": eta,
            "timestamp": time.time(),
        }

    def _clear_download_progress(self, model_name: str):
        """Limpa o progresso do download"""
        if model_name in self.download_progress:
            del self.download_progress[model_name]
