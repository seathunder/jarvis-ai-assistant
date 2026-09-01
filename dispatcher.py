import json
import requests
from config import OPENROUTER_API_KEY, logger
from research import perform_local_research
from executor import agentic_feedback_loop
from projects import ProjectManager
from computer_use import take_desktop_screenshot, move_and_click, type_text

DISPATCHER_SYSTEM_PROMPT = """You are the central routing core of the Jarvis autonomous framework. Your ONLY job is to analyze the user's prompt and determine the required execution pipeline. You must return a valid JSON object matching the schema below. NEVER output conversational text.

Definitions:
- 'SMALL': Basic Q&A, simple math, checking calendar, reading text.
- 'LARGE': Requires web searching, scraping, multi-step agentic coding, reading files, or accessing the local OS sandbox.

Required JSON Schema:
{
  "task_complexity": "SMALL" | "LARGE",
  "required_engine": "LOCAL_SLM" | "GEMINI_FLASH" | "GEMINI_PRO",
  "tools_required": ["web_search", "os_interpreter", "project_creator", "desktop_control", "none"],
  "pipeline_routing_tag": "fast_response" | "agentic_loop" | "research_loop" | "project_loop" | "desktop_loop"
}

Engine Rules:
- Route to 'research_loop' if the user asks for web research, current news, live search, or information lookup.
- Route to 'project_loop' if the user asks to build, create, or initialize a software project.
- Route to 'agentic_loop' if code execution, python script running, or self-healing retries are needed.
- Route to 'desktop_loop' if taking screenshots, clicking desktop coordinates, or typing text into desktop apps is requested.
- Use LOCAL_SLM for private or small tasks; GEMINI_FLASH for research/agent loops; GEMINI_PRO for complex architecture.
"""

def triage_task(user_prompt):
    if not OPENROUTER_API_KEY:
        logger.error("No OpenRouter API key found.")
        return {"error": "Missing OpenRouter API Key"}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {"role": "system", "content": DISPATCHER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error during triage: {e}")
        low = user_prompt.lower()
        if any(w in low for w in ["search", "find", "news", "research"]):
            return {"task_complexity": "LARGE", "required_engine": "GEMINI_FLASH", "tools_required": ["web_search"], "pipeline_routing_tag": "research_loop"}
        if any(w in low for w in ["screenshot", "desktop", "click"]):
            return {"task_complexity": "LARGE", "required_engine": "LOCAL_SLM", "tools_required": ["desktop_control"], "pipeline_routing_tag": "desktop_loop"}
        return {"error": str(e)}

def mock_code_generator(prompt):
    if "fail once" in prompt.lower() and "Previous attempt" not in prompt:
        return "print(undefined_variable)"
    return "print('Hello from J.A.R.V.I.S. Agentic Loop!')"

def process_prompt(user_prompt, context=[]):
    triage_result = triage_task(user_prompt)
    logger.info(f"Triage Result: {triage_result}")
    
    if "error" in triage_result and "pipeline_routing_tag" not in triage_result:
        return f"Error during triage: {triage_result['error']}"

    routing_tag = triage_result.get("pipeline_routing_tag", "fast_response")
    tools = triage_result.get("tools_required", [])
    
    # 1. Local Web Search & GraphRAG Route
    if routing_tag == "research_loop" or "web_search" in tools:
        logger.info("Triggering Local WebSearch & GraphRAG Engine...")
        graph_context = perform_local_research(user_prompt)
        return f"🔎 **Local GraphRAG Research Completed**\n\n```json\n{graph_context[:1500]}\n...\n```\n\n*(Full Graph Context extracted & delivered to model)*"

    # 2. Desktop OS Control Route
    elif routing_tag == "desktop_loop" or "desktop_control" in tools:
        logger.info("Triggering Desktop Control Module...")
        if "screenshot" in user_prompt.lower():
            path = take_desktop_screenshot()
            return f"🖥️ **Desktop Screenshot Captured!**\nSaved at: `{path}`"
        return "🖥️ **Desktop Action Triggered.**"

    # 3. Agentic Feedback & Execution Sandbox Route
    elif routing_tag == "agentic_loop" or "os_interpreter" in tools:
        logger.info("Triggering Agentic Execution Sandbox...")
        result = agentic_feedback_loop(mock_code_generator, user_prompt)
        if result["success"]:
            return f"⚡ **Agentic Execution Succeeded** (Attempt {result['attempts']})\n\n**Output:**\n```\n{result['output']}\n```"
        else:
            return f"❌ **Agentic Execution Failed:** {result['error']}"

    # 4. Autonomous Project Creation Route
    elif routing_tag == "project_loop" or "project_creator" in tools:
        project_name = user_prompt.split()[-1] if user_prompt.split() else "new_project"
        pm = ProjectManager(project_name)
        path = pm.create_project(description=user_prompt)
        pm.write_file("main.py", "# Auto-generated by J.A.R.V.I.S.\nprint('Project Initialized')\n")
        return f"🛠️ **Project Created Successfully!**\nPath: `{path}`\nInitialized `project.json` and `main.py`."

    # 5. Standard Fast Response Route
    else:
        return f"🤖 **Jarvis Fast Response**: Received your query: '{user_prompt}'."
