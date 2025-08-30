# services/llm_extract_service.py
from typing import Any, Dict, Optional
import json
import re
from google.cloud import aiplatform
from openai import OpenAI


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
    - Do NOT include <think> sections or any hidden reasoning.
    - Output ONLY the required JSON.
    Return ONLY a compact JSON with this schema:
    {{
    "complexity_level": "Ordinary complexity|Complexity that is more than ordinary but not high|High complexity",
    "reasoning": "very short explanation (<=40 words)"
    }}

    Rules:
    - "Ordinary Complexity": These items are for the consultation, investigation (if required) and management of a single system issue in a patient
with no relevant comorbidities where the differential diagnosis is limited.Includes targeted history and examination, interpretation of relevant investigations (if required), development and
initiation of a management plan, relevant GP and specialist communication and associated documentation. These
patients would typically be discharged home from the Emergency Department. A period of observation is not
required for these patients
    - "Complexity More than Ordinary but Not High":These items are for the assessment, investigation and management of an undifferentiated presentation or a
presentation with a clear diagnosis that needs risk stratification and complication exclusion. Where the diagnosis is
clear from the outset, this item should be used when management is time consuming or more than one strategy is
required. The attendance may include referral or consultation with alternate specialist(s). These patients may or may
not be admitted.
Includes a period of observation in response to initial treatment and / or requiring results of investigations to inform
an ongoing management plan, and includes any routine point-of-care procedures (such as ECGs, in-dwelling urinary
catheterisation, venous and arterial blood gas sampling, ultrasound in conjunction with procedures such as vascular
access or nerve block).
For patients requiring a prolonged period of observation, admission to an emergency department short stay unit may
be required.

    - "High Complexity": These items are for the assessment, investigation and management of an undifferentiated ED patient with one or
more comorbidities and more than one differential diagnosis.
These items may include time consulting with alternate specialists, liaising with community services and
arrangement of admission, pharmacy reconciliation, communication with family, carers and general practitioners;
and any routine point-of-care procedures (such as ECGs, in-dwelling urinary catheterisation, venous and arterial
blood gas sampling, ultrasound in conjunction with procedures such as vascular access or nerve block).
For patients requiring a prolonged period of observation, admission to an emergency department short stay unit may
be required.

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
            client = OpenAI()
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,               
            )
            # response = self.endpoint.predict(instances=instances, parameters=params)
        except Exception as e:
            raise RuntimeError(f"Prediction call failed: {e}")

        if response.output_text:
            print("====================LLM extract succeeded==============")
            response_text = response.output_text.strip()
            if response_text.startswith("```"):
                m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text, flags=re.IGNORECASE)
                if m:
                    response_text = m.group(1).strip()

            print(response_text)
            # model response
            output = json.loads(response_text)


            complexity_level = output.get("complexity_level", "")
            reasoning = output.get("reasoning", "")
            raw_text = str(output)

            return {
                "complexity_level": complexity_level,
                "reasoning": reasoning,
                "raw_text": raw_text,
                # "truncated": truncated,  # True if model hit length limit
            }


# llmextractservice = LLMExtractService()
# # print(llmextractservice._build_prompt("Test note"))  # sanity check
# print(llmextractservice.predict_complexity("Test note"))  # sanity check