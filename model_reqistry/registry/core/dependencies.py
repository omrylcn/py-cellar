from registry.services import ModelRegistry
from registry.core.registry import registry_container


async def get_registry() -> ModelRegistry:
    """FastAPI dependency for getting registry instance"""
    return await registry_container.get_registry()
