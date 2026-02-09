"""
Configuration Management for Enterprise Document Q&A System

Centralized configuration using Pydantic V2 with environment variable support.
Supports both .env file and environment variable configuration.
"""

import os
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Application configuration management.
    
    Automatically loads from:
    1. Environment variables
    2. .env file in project root
    """
    
    # =========================================================================
    # NVIDIA API Configuration
    # =========================================================================
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    
    # =========================================================================
    # Model Configuration
    # =========================================================================
    nvidia_embedding_model: str = "nvidia/nv-embed-v1"
    nvidia_llm_model: str = "meta/llama-3.1-8b-instruct"
    
    # =========================================================================
    # Vector Store & Data Paths
    # =========================================================================
    vector_store_path: str = "./data/vector_store"
    raw_docs_path: str = "./data/raw_docs"
    
    # =========================================================================
    # Chunking Configuration (Production-optimized)
    # =========================================================================
    chunk_size: int = 1200  # Larger chunks preserve more context
    chunk_overlap: int = 300  # More overlap for semantic continuity
    
    # =========================================================================
    # Retrieval Configuration
    # =========================================================================
    top_k: int = 4  # Number of chunks to retrieve per query
    
    # =========================================================================
    # Server Configuration
    # =========================================================================
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # =========================================================================
    # Logging Configuration
    # =========================================================================
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global config instance
config = Config()


def validate_config() -> bool:
    """
    Validate critical configuration.
    
    Returns:
        bool: True if valid, raises Exception otherwise
    """
    if not config.nvidia_api_key:
        raise ValueError(
            "NVIDIA_API_KEY not set. Please set it in .env or environment variables."
        )
    
    os.makedirs(config.vector_store_path, exist_ok=True)
    os.makedirs(config.raw_docs_path, exist_ok=True)
    
    return True
