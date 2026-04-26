"""
SCSC - Sistema de Ciberseguridad Cuántica
Módulo de componentes compartidos
"""

__version__ = "0.1.0"
__author__ = "SCSC Team"

from .config import Config
from .protocols import Message, MessageType, Protocol
from .logger import setup_logger, get_logger
from .utils import (
    generate_node_id,
    calculate_checksum,
    format_bytes,
    get_timestamp,
    serialize_json,
    deserialize_json
)

__all__ = [
    "Config",
    "Message",
    "MessageType",
    "Protocol",
    "setup_logger",
    "get_logger",
    "generate_node_id",
    "calculate_checksum",
    "format_bytes",
    "get_timestamp",
    "serialize_json",
    "deserialize_json"
]