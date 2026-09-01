import subprocess
import os
import sys
import tempfile
from config import logger

def execute_python_code(code_str, timeout=15):
    """
    Executes raw python code string in a subprocess.
    Returns (success: bool, stdout: str, stderr: str).
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code_str)
        temp_path = temp_file.name
        
    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        success = (result.returncode == 0)
        return success, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Execution timed out."
    except Exception as e:
        return False, "", str(e)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def agentic_feedback_loop(code_generator_func, initial_prompt, max_retries=3):
    """
    Agentic Feedback Loop:
    1. Generates code via code_generator_func.
    2. Executes the code locally.
    3. If execution fails, passes stderr back to code_generator_func for self-correction.
    4. Repeats up to max_retries.
    """
    current_prompt = initial_prompt
    history = []
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"Agentic Execution Attempt {attempt}/{max_retries}...")
        code = code_generator_func(current_prompt)
        
        success, stdout, stderr = execute_python_code(code)
        
        if success:
            logger.info("Code executed successfully!")
            return {
                "success": True,
                "attempts": attempt,
                "output": stdout,
                "code": code
            }
            
        logger.warning(f"Attempt {attempt} failed with error:\n{stderr}")
        history.append({"attempt": attempt, "code": code, "error": stderr})
        
        # Prepare feedback prompt for self-healing
        current_prompt = f"""
Previous attempt #{attempt} failed with error:
{stderr}

Failed Code:
```python
{code}
```

Please fix the error and return ONLY the updated Python code block.
"""

    return {
        "success": False,
        "attempts": max_retries,
        "error": "Max retries reached without resolution.",
        "history": history
    }
