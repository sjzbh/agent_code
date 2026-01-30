"""
Utils for the Virtual Software Company
Contains utility functions including prompt loading
"""
import yaml
import json
import re
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
    Clean JSON text by removing markdown code blocks and handling common issues
    Args:
        text: Text that may contain JSON in markdown code blocks
    Returns:
        Cleaned JSON text
    """
    # Remove markdown code block markers
    text = re.sub(r'```json\s*', '', text)  # Remove ```json
    text = re.sub(r'```\s*', '', text)      # Remove remaining ```

    # Remove extra whitespace and normalize
    text = text.strip()

    # Handle common issues with JSON responses
    # Remove any trailing text after closing brace
    if text.count('{') == text.count('}'):
        # Find the position of the last matching closing brace
        brace_count = 0
        last_brace_pos = -1
        for i, char in enumerate(text):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    last_brace_pos = i

        if last_brace_pos != -1:
            text = text[:last_brace_pos+1]

    return text

def safe_json_parse(text: str, default_return: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Safely parse JSON text with fallback to default object
    Args:
        text: Text to parse as JSON
        default_return: Default object to return if parsing fails
    Returns:
        Parsed JSON object or default object
    """
    if default_return is None:
        default_return = {}

    try:
        # Clean the text first
        cleaned_text = clean_json_text(text)

        # Try to parse the JSON
        parsed_json = json.loads(cleaned_text)
        return parsed_json
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract JSON from the text using multiple strategies
        try:
            # Strategy 1: Look for JSON structure between curly braces
            brace_count = 0
            start_idx = -1
            end_idx = -1

            for i, char in enumerate(cleaned_text):
                if char == '{':
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        end_idx = i
                        break

            if start_idx != -1 and end_idx != -1:
                json_str = cleaned_text[start_idx:end_idx+1]
                return json.loads(json_str)
        except:
            pass

        try:
            # Strategy 2: Use regex to find JSON-like structure
            import re
            json_match = re.search(r'\{(?:[^{}]|{[^{}]*})*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        try:
            # Strategy 3: Alternative regex for nested structures
            import re
            pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(pattern, text)
            if matches:
                # Try each match until one parses correctly
                for match in matches:
                    try:
                        return json.loads(match)
                    except:
                        continue
        except:
            pass

        # If all parsing attempts fail, return the default object
        return default_return
    except Exception:
        # For any other exception, return the default object
        return default_return