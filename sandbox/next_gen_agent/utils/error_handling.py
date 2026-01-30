
"""
Error Handling Utilities - Generated based on common error patterns
"""
import functools
import traceback
from typing import Callable, Any

def safe_execute(func: Callable) -> Callable:
    """Decorator to safely execute functions with error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(f"文件未找到: {e}")
            return {"success": False, "error": f"文件未找到: {e}"}
        except PermissionError as e:
            print(f"权限错误: {e}")
            return {"success": False, "error": f"权限错误: {e}"}
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return {"success": False, "error": f"JSON解析错误: {e}"}
        except Exception as e:
            print(f"执行错误: {e}")
            traceback.print_exc()
            return {"success": False, "error": f"执行错误: {e}"}
        return result

def safe_json_parse(text: str, default_return: dict = None):
    """Safely parse JSON with fallback to default object"""
    if default_return is None:
        default_return = {}

    try:
        # Clean the text first
        import re
        cleaned_text = re.sub(r"```json\s*", "", text)  # Remove ```json
        cleaned_text = re.sub(r"```", "", cleaned_text)   # Remove remaining ```
        cleaned_text = cleaned_text.strip()

        import json
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Try to extract JSON from text if direct parsing fails
        try:
            import re
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return default_return
    except Exception:
        return default_return
