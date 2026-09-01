import json
import requests
from config import OPENROUTER_API_KEY, logger

DISPATCHER_SYSTEM_PROMPT = """You are the central routing core of the Jarvis autonomous framework. Your ONLY job is to analyze the user's prompt and determine the required execution pipeline. You must return a valid JSON object matching the schema below. NEVER output conversational text.

Definitions:
- 'SMALL': Basic Q&A, simple math, checking calendar, reading text.
- 'LARGE': Requires web searching, scraping, multi-step agentic coding, reading files, or accessing the local OS sandbox.

Required JSON Schema:
{
  "task_complexity": "SMALL" | "LARGE",
  "required_engine": "LOCAL_SLM" | "GEMINI_FLASH" | "GEMINI_PRO",
  "tools_required": ["web_search", "os_interpreter", "whatsapp_send", "none"],
  "pipeline_routing_tag": "fast_response" | "agentic_loop"
}

Engine Rules:
- Use LOCAL_SLM if the task requires NO live internet or is highly private.
- Use GEMINI_FLASH for Large tasks requiring web search or standard agent loops.
- Use GEMINI_PRO ONLY if the task involves dense code architecture, complex math reasoning, or debugging a multi-file script.
"""

def triage_task(user_prompt):
    """
    Calls the OpenRouter API to determine the task complexity and routing strategy.
    For this example, we use a free open-weights model.
    """
    if not OPENROUTER_API_KEY:
        logger.error("No OpenRouter API key found.")
        return {"error": "Missing OpenRouter API Key"}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # We use a fast, free model for triage
    data = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {"role": "system", "content": DISPATCHER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        try:
            parsed_json = json.loads(content)
            return parsed_json
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Dispatcher: {content}")
            return {"error": "Invalid JSON from Dispatcher", "raw": content}
            
    except Exception as e:
        logger.error(f"Error during triage: {e}")
        return {"error": str(e)}

def process_prompt(user_prompt, context=[]):
    """
    Main processing function.
    1. Triages the prompt.
    2. Routes it to the correct pipeline based on the triage result.
    """
    triage_result = triage_task(user_prompt)
    logger.info(f"Triage Result: {triage_result}")
    
    if "error" in triage_result:
        return f"Error during processing: {triage_result['error']}"

    routing_tag = triage_result.get("pipeline_routing_tag")
    complexity = triage_result.get("task_complexity")
    engine = triage_result.get("required_engine")
    tools = triage_result.get("tools_required", [])
    
    # Stub: Actual execution pipelines will go here in future phases.
    response_msg = f"Task Triaged.\nComplexity: {complexity}\nEngine: {engine}\nTools: {', '.join(tools)}\nRouting to: {routing_tag} pipeline.\n\n"
    
    if routing_tag == "fast_response":
        response_msg += "[MOCK] Fast Response: I've processed your request locally."
    elif routing_tag == "agentic_loop":
        response_msg += "[MOCK] Agentic Loop: Initiating background tasks..."
        if "web_search" in tools:
            response_msg += " (Will perform web search)"
    else:
        response_msg += f"Unknown routing tag: {routing_tag}"
        
    return response_msg
