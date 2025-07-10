"""
Configuration settings for SUMO Helper Backend
Environment-based configuration with production defaults
"""

import os
from typing import List

class Config:
    """Base configuration class"""
    
    # Application settings
    APP_NAME = "SUMO Helper API"
    APP_VERSION = "1.0.0"
    DEBUG = False
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # CORS settings
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "sumo_helper.log")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File storage settings
    STATIC_DIR = "static"
    MAPS_DIR = os.path.join(STATIC_DIR, "maps")
    NETWORKS_DIR = os.path.join(STATIC_DIR, "networks")
    SIMULATIONS_DIR = os.path.join(STATIC_DIR, "simulations")
    UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
    
    # OSM settings
    OSM_TIMEOUT = int(os.getenv("OSM_TIMEOUT", "30"))
    OSM_MAX_AREA_SIZE = float(os.getenv("OSM_MAX_AREA_SIZE", "0.01"))
    OSM_ROAD_FILTER = os.getenv("OSM_ROAD_FILTER", "motorway|trunk|primary|secondary")
    
    # SUMO settings
    SUMO_HOME = os.getenv("SUMO_HOME", "/usr/share/sumo")
    SUMO_GUI_PATH = os.getenv("SUMO_GUI_PATH", "sumo-gui")
    SUMO_PATH = os.getenv("SUMO_PATH", "sumo")
    
    # Simulation settings
    DEFAULT_SIMULATION_TIME = int(os.getenv("DEFAULT_SIMULATION_TIME", "3600"))
    MAX_SIMULATION_TIME = int(os.getenv("MAX_SIMULATION_TIME", "7200"))
    
    # Rate limiting (optional)
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    
    # Development-specific settings
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    
    # Production-specific settings
    RATE_LIMIT_ENABLED = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    
    # Test-specific settings
    STATIC_DIR = "test_static"
    MAPS_DIR = os.path.join(STATIC_DIR, "maps")
    NETWORKS_DIR = os.path.join(STATIC_DIR, "networks")
    SIMULATIONS_DIR = os.path.join(STATIC_DIR, "simulations")

# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return config_map.get(env, DevelopmentConfig)() 