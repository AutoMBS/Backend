#!/usr/bin/env python3
"""
Configuration file for the JSON to YAML LLM Converter
"""

import os
from typing import Optional

class Config:
    """Configuration class for the converter"""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"  # or "gpt-4o" for better quality
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 4000
    
    # Processing Configuration
    TEST_MODE: bool = False  # Set to False for production
    MAX_TEST_ITEMS: int = 100
    BATCH_SIZE: int = 10
    
    # File Paths
    INPUT_DIR: str = "extracted_categories"
    OUTPUT_DIR: str = "yaml_rules_llm"
    
    # Category Names
    CATEGORY_NAMES = {
        "1": "Professional Attendance",
        "2": "Diagnostic Procedures and Investigations",
        "3": "Therapeutic Procedures", 
        "4": "Diagnostic Imaging",
        "5": "Pathology",
        "6": "Anaesthesia",
        "8": "Other Medical Services"
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            print("❌ Error: OPENAI_API_KEY not set")
            print("Please set your OpenAI API key:")
            print("export OPENAI_API_KEY='your-api-key-here'")
            return False
        
        if not os.path.exists(cls.INPUT_DIR):
            print(f"❌ Error: Input directory '{cls.INPUT_DIR}' not found")
            return False
        
        print("✅ Configuration validated successfully")
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("Current Configuration:")
        print(f"  OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"  Temperature: {cls.OPENAI_TEMPERATURE}")
        print(f"  Max Tokens: {cls.OPENAI_MAX_TOKENS}")
        print(f"  Test Mode: {cls.TEST_MODE}")
        print(f"  Input Directory: {cls.INPUT_DIR}")
        print(f"  Output Directory: {cls.OUTPUT_DIR}")
        print(f"  Categories: {len(cls.CATEGORY_NAMES)}")

if __name__ == "__main__":
    Config.print_config()
    Config.validate()
