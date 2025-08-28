# services/llm_extract_service.py
from typing import Any, Dict, Optional
import json
import re
from google.cloud import aiplatform


PROJECT_ID = "thematic-keel-470306-f6"
REGION = "us-east1"  # e.g., "us-central1"
ENDPOINT_ID = "3651992687285895168" # Get this from the Console (Vertex AI -> Endpoints)


class LLMExtractService:
    """
    调用 Vertex AI Endpoint，根据 note 判定 complexity level。
    返回统一结构：{"complexity_level": "Ordinary complexity|Complexity that is more than ordinary but not high|High complexity", "reasoning": "...", "raw_text": "..."}
    """

    def __init__(
        self,
        project_id: str = PROJECT_ID,
        region: str = REGION,
        endpoint_id: str = ENDPOINT_ID,
        *,
        temperature: float = 0.7,
        max_output_tokens: int = 64000,
    ) -> None:
        self.project_id = project_id
        self.region = region
        self.endpoint_id = endpoint_id
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def _build_prompt(self, note: str) -> str:
    # Constrain model to return compact JSON (names unchanged; no mapping)
        return f"""
    You are a medical triage assistant. Read the following clinical note and estimate its **complexity level**.

    Return ONLY a compact JSON with this schema:
    {{
    "complexity_level": "Ordinary complexity|Complexity that is more than ordinary but not high|High complexity",
    "reasoning": "very short explanation (<=40 words)"
    }}

    Rules:
    - "Ordinary Complexity": single-system issue, no comorbidities, limited differential. Involves targeted history/exam, relevant investigations if needed, management plan, and discharge home. No observation required.

    - "Complexity More than Ordinary but Not High": undifferentiated presentation or clear diagnosis needing risk stratification/complication exclusion. Time-consuming or multi-strategy management, may include observation, routine point-of-care procedures (ECG, catheter, blood gases, ultrasound with access). Admission possible, sometimes short-stay.

    - "High Complexity": undifferentiated patient with comorbidities and multiple differentials. Requires specialist consultation, community/service liaison, admission planning, pharmacy reconciliation, and family/GP communication. Routine point-of-care procedures as above. Often prolonged observation or short-stay admission required.

    Note:
    \"\"\"{note.strip()}\"\"\"
    """

    def predict_complexity(self, note: str) -> Dict[str, Any]:

        # Init client + endpoint
        aiplatform.init(project=self.project_id, location=self.region)
        endpoint_resource_name = (
            f"projects/{self.project_id}/locations/{self.region}/endpoints/{self.endpoint_id}"
        )

        try:
            self.endpoint = aiplatform.Endpoint(endpoint_name=endpoint_resource_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Vertex AI Endpoint: {e}")

        # Build chatCompletions-style request (the only working format for your model)
        prompt = self._build_prompt(note)
        instances = [{
            "@requestFormat": "chatCompletions",
            "messages": [{"role": "user", "content": prompt}],
            # decoding params must be INSIDE the instance for this endpoint
            "max_token": getattr(self, "max_output_tokens", 64000),
            "temperature": getattr(self, "temperature", 0.7),
            "top_p": 1.0,
            "top_k": -1,
        }]
        params: Dict[str, Any] = {}  # container ignores parameters

        try:
            response = self.endpoint.predict(instances=instances, parameters=params)
        except Exception as e:
            raise RuntimeError(f"Prediction call failed: {e}")

        if response.predictions:

            # Normalize predictions to a dict
            pred_container = getattr(response, "predictions", None)
            if isinstance(pred_container, list):
                pred0 = pred_container[0] if pred_container else {}
            elif isinstance(pred_container, dict):
                pred0 = pred_container
            else:
                pred0 = {}

            # Pull OpenAI-style content
            choices = pred0.get("choices", []) if isinstance(pred0, dict) else []
            content = choices[0].get("message", {}).get("content", "") if choices else ""
            finish_reason = choices[0].get("finish_reason") if choices else None
            truncated = (finish_reason == "length")
            raw_text = content  # keep full assistant message for audit/debug

            # Remove optional <think>...</think>
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()

            # Find the last balanced JSON object
            def _find_last_json(s: str) -> Optional[str]:
                end = None
                depth = 0
                for i in range(len(s) - 1, -1, -1):
                    ch = s[i]
                    if ch == '}':
                        if depth == 0:
                            end = i
                        depth += 1
                    elif ch == '{':
                        depth -= 1
                        if depth == 0 and end is not None:
                            return s[i:end + 1]
                return None

            json_str = _find_last_json(content)

            complexity_level = ""
            reasoning = ""
            if json_str:
                try:
                    parsed = json.loads(json_str)
                    complexity_level = str(parsed.get("complexity_level", "")).strip()  # no mapping
                    reasoning = str(parsed.get("reasoning", "")).strip()
                except Exception:
                    pass  # keep defaults if JSON parsing fails

            return {
                "complexity_level": complexity_level,
                "reasoning": reasoning,
                "raw_text": raw_text,
                "truncated": truncated,  # True if model hit length limit
            }


# llmextractservice = LLMExtractService()
# # print(llmextractservice._build_prompt("Test note"))  # sanity check
# print(llmextractservice.predict_complexity("Test note"))  # sanity check