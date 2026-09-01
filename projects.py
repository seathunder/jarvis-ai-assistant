import os
import json
from config import logger

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "projects")

def ensure_projects_dir():
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR)

class ProjectManager:
    """
    Manages autonomous project creation, directory trees, and task files.
    """
    def __init__(self, project_name):
        ensure_projects_dir()
        self.name = project_name.lower().replace(" ", "_")
        self.project_path = os.path.join(PROJECTS_DIR, self.name)
        
    def create_project(self, description=""):
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)
            
        manifest = {
            "name": self.name,
            "description": description,
            "tasks": [
                {"id": 1, "task": "Initialize project structure", "status": "COMPLETED"},
                {"id": 2, "task": "Implement core logic", "status": "PENDING"}
            ]
        }
        
        manifest_path = os.path.join(self.project_path, "project.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        logger.info(f"Project '{self.name}' created at {self.project_path}")
        return self.project_path

    def write_file(self, relative_filepath, content):
        target_path = os.path.join(self.project_path, relative_filepath)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Wrote file: {target_path}")
        return target_path

    def get_manifest(self):
        manifest_path = os.path.join(self.project_path, "project.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                return json.load(f)
        return None
