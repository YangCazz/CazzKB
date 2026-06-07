from app.config import AppConfig, load_config
from app.retrieval.embeddings import get_embedding_provider
from app.kb_manager.manager import KBManager


_config: AppConfig | None = None
_kb_manager: KBManager | None = None


def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_kb_manager() -> KBManager:
    global _kb_manager
    if _kb_manager is None:
        config = get_config()
        embed = get_embedding_provider(
            factory=config.embedding.factory,
            model=config.embedding.model,
            api_key=config.embedding.api_key,
            base_url=config.embedding.base_url,
        )
        _kb_manager = KBManager(config, embed)
    return _kb_manager
