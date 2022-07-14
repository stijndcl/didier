from abc import ABC, abstractmethod

import discord
from pydantic import BaseModel

__all__ = [
    "EmbedBaseModel",
    "EmbedPydantic",
]


class EmbedBaseModel(ABC):
    """Abstract base class for a model that can be turned into a Discord embed"""

    @abstractmethod
    def to_embed(self) -> discord.Embed:
        """Turn this model into a Discord embed"""
        raise NotImplementedError


class EmbedPydantic(EmbedBaseModel, BaseModel, ABC):
    """Pydantic version of EmbedModel"""
