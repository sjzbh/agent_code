"""
Utils for the Virtual Software Company
Contains utility functions including prompt loading
"""
import yaml
import json
from typing import Dict, Any
from pathlib import Path

def load_prompt(prompt_path: str) -> Dict[str, Any]:
    """
    Load prompt templates from YAML or JSON file
    Args:
        prompt_path: Path to the prompt template file
    Returns:
        Dictionary containing prompt templates
    """
    path = Path(prompt_path)
    
    if path.suffix.lower() in ['.yaml', '.yml']:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    elif path.suffix.lower() == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

def call_llm(config: Dict[str, Any], prompt: str) -> str:
    """
    Call LLM with given config and prompt
    Args:
        config: Configuration for the LLM
        prompt: Prompt to send to the LLM
    Returns:
        Response from the LLM
    """
    # This is a simplified version - in the actual implementation,
    # this would interface with the AI client manager
    client = config.get('client')
    if client:
        # Actual implementation would call the client
        # For now, returning a placeholder
        return f"LLM Response to: {prompt[:50]}..."
    else:
        return "Client not initialized"

def clean_json_text(text: str) -> str:
    """
    Clean JSON text by removing markdown code blocks
    Args:
        text: Text that may contain JSON in markdown code blocks
    Returns:
        Cleaned JSON text
    """
    # Remove markdown code block markers
    text = text.replace('```json', '').replace('```', '')
    # Remove extra whitespace
    return text.strip()