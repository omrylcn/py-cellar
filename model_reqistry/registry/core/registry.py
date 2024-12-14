from typing import Optional
from fastapi import HTTPException,status

from registry.services import ModelRegistry
from registry.logger import logger

class RegistryContainer:
    def __init__(self):
        self._registry: Optional[ModelRegistry] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize registry if not already initialized"""
        if not self._initialized:
            try:
                self._registry = ModelRegistry()
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize registry: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initialize model registry",
                )

    async def get_registry(self) -> ModelRegistry:
        """Get or initialize registry instance"""
        if not self._initialized:
            await self.initialize()
        return self._registry


registry_container = RegistryContainer()
