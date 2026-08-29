import re
from pathlib import Path
from typing import Any, Optional
import yaml


class PromptRegistry:
    """
    Prompt Versioning and Template Management Registry.
    Loads, tracks, and renders versioned LLM prompts with variable validation.
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        root = Path(__file__).resolve().parents[2]
        self.prompts_dir = Path(prompts_dir) if prompts_dir else (root / "prompts")
        self._templates: dict[str, dict[str, Any]] = {}
        self._load_all_templates()

    def _load_all_templates(self):
        """Discovers and parses all YAML prompt templates."""
        if not self.prompts_dir.exists():
            return

        for yaml_file in self.prompts_dir.glob("*/*.yaml"):
            agent_name = yaml_file.parent.name
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    version = data.get("version", yaml_file.stem)
                    key = f"{agent_name}:{version}"
                    self._templates[key] = data
                    # Also map as default 'latest'
                    self._templates[f"{agent_name}:latest"] = data
            except Exception as e:
                print(f"Error loading prompt template {yaml_file}: {e}")

    def get_template(self, agent_name: str, version: str = "latest") -> dict[str, Any]:
        """Retrieves raw template schema by agent and version."""
        key = f"{agent_name}:{version}"
        if key not in self._templates:
            # Fallback to latest
            key_latest = f"{agent_name}:latest"
            if key_latest in self._templates:
                return self._templates[key_latest]
            raise KeyError(f"Prompt template '{key}' not found in registry.")
        return self._templates[key]

    def render(self, agent_name: str, variables: dict[str, Any], version: str = "latest") -> dict[str, str]:
        """
        Hydrates template placeholders {{ variable }} with supplied values.
        """
        template = self.get_template(agent_name, version)
        sys_prompt = template.get("system_prompt", "").strip()
        user_tpl = template.get("user_template", "").strip()

        # Variable validation
        req_vars = template.get("input_variables", [])
        for v in req_vars:
            if v not in variables:
                variables[v] = f"[UNSPECIFIED_{v}]"

        rendered_user = user_tpl
        for k, v in variables.items():
            pattern = re.compile(r"\{\{\s*" + re.escape(k) + r"\s*\}\}")
            rendered_user = pattern.sub(str(v), rendered_user)

        return {
            "version": template.get("version", "1.0.0"),
            "agent": agent_name,
            "system_prompt": sys_prompt,
            "user_prompt": rendered_user,
        }
