# services/llm_reasoning_service.py
from typing import Any, Dict, List, Optional
import json
import re
from google.cloud import aiplatform
from openai import OpenAI
import re
PROJECT_ID = "thematic-keel-470306-f6"
REGION = "us-east1"  # e.g., "us-central1"
ENDPOINT_ID = "3651992687285895168" # Get this from the Console (Vertex AI -> Endpoints)


class LLMReasoningService:
    """
    Call Vertex AI Endpoint to select the most appropriate medical coding item based on RAG candidates.
    Optimized for medical coding scenarios with precise reasoning in English.
    Returns: {"selected_item": {...}, "reasoning": "...", "confidence": 0.95, "raw_text": "..."}
    """

    def __init__(
        self,
        project_id: str = PROJECT_ID,
        region: str = REGION,
        endpoint_id: str = ENDPOINT_ID,
        *,
        temperature: float = 0.5,  # Very low temperature for precise medical reasoning
        max_output_tokens: int = 64000,
    ) -> None:
        self.project_id = project_id
        self.region = region
        self.endpoint_id = endpoint_id
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def _build_prompt(self, patient_info: str, candidates: List[Dict[str, Any]]) -> str:
        """
        Build medical coding reasoning prompt
        
        Args:
            patient_info: Patient clinical information (like Figure 1 format)
            candidates: RAG returned medical coding candidates (like Figure 2 format)
        """
        candidates_str = ""
        for i, candidate in enumerate(candidates):
            score = candidate.get("score", 0)
            payload = candidate.get("payload", {})
            
            # Build candidate medical coding item description
            item_desc = f"Candidate {i+1} (Score: {score:.3f}):\n"
            
            # Extract key information from payload
            if "item_number" in payload:
                item_desc += f"- Item Number: {payload.get('item_number', 'N/A')}\n"
            elif "item_num" in payload:
                item_desc += f"- Item Number: {payload.get('item_num', 'N/A')}\n"
            if "category_name" in payload:
                item_desc += f"- Category: {payload.get('category_name', 'N/A')}\n"
            if "group_name" in payload:
                item_desc += f"- Group: {payload.get('group_name', 'N/A')}\n"
            if "service_provider" in payload:
                item_desc += f"- Provider: {payload.get('service_provider', 'N/A')}\n"
            if "location" in payload:
                item_desc += f"- Location: {payload.get('location', 'N/A')}\n"
            if "start_age" in payload and "end_age" in payload:
                item_desc += f"- Age Range: {payload.get('start_age', 'N/A')}-{payload.get('end_age', 'N/A')}\n"
            if "start_time" in payload and "end_time" in payload:
                item_desc += f"- Duration: {payload.get('start_time', 'N/A')}-{payload.get('end_time', 'N/A')} min\n"
            elif "start_duration" in payload and "end_duration" in payload:
                item_desc += f"- Duration: {payload.get('start_duration', 'N/A')}-{payload.get('end_duration', 'N/A')} min\n"
            
            candidates_str += item_desc + "\n"
        
        return f"""You are a medical item claiming expert. Choose the single most appropriate item from the candidates.

Patient Information:
{patient_info.strip()}

Candidate Medical Codes (array; each has fields like item_num, service_summary, age_range, provider, location, duration_rules, rag_score, etc.):
{candidates_str.strip()}

Decision rules:
- Prioritize the candidate’s **service_summary** as the primary determinant of clinical fit.
- Then verify: age appropriateness, provider type, location suitability, duration requirements, and RAG similarity score.
- Be precise and conservative. Do not invent facts; use only visible patient evidence.
- If multiple items are eligible, tie-break by: (1) best match to service_summary; (2) stricter/ more specific criteria; (3) higher rag_score; (4) most recent/valid descriptor.

Return ONLY compact JSON with keys in this exact order:
{{
  "selected_item_index": 0,
  "decision": "item_number or item_num of the chosen candidate",
  "why": "Start with the candidate's service_summary and state WHY it matches in <=2 sentences.And then please state the evidence match and extract some key evident from the patient information.",
  "evidence_match": {{
    "clinical": "1 short clause mapping patient presentation to service_summary",
    "age": "e.g., 42 within [0-200]",
    "provider": "e.g., GP matches provider requirement",
    "location": "e.g., consulting rooms match",
    "duration": "e.g., visit <= 10 min meets threshold or N/A",
    "rag_score": "e.g., 0.83 higher than others"
  }},
  "key_factors": ["key_factor1", "key_factor2", "key_factor3"],
  "confidence": 0.8
}}

Formatting constraints:
- selected_item_index MUST be an integer in [0, 2].
- Keep "why" concise (<=2 sentences) and start by analyzing the **service_summary**.
- Keep evidence_match values to short phrases (no narratives).
- Output STRICT JSON only, no extra text.
"""

    def select_best_item(
        self, 
        patient_info: str, 
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Select the most appropriate medical coding item based on patient information
        
        Args:
            patient_info: Patient clinical information (English text)
            candidates: RAG returned medical coding candidates
            
        Returns:
            Dict containing selected item, reasoning and confidence
        """
        if not candidates:
            return {
                "error": "No candidate items to analyze",
                "selected_item": None,
                "reasoning": "",
                "confidence": 0.0,
                "raw_text": ""
            }

        # Init client + endpoint
        aiplatform.init(project=self.project_id, location=self.region)
        endpoint_resource_name = (
            f"projects/{self.project_id}/locations/{self.region}/endpoints/{self.endpoint_id}"
        )

        try:
            self.endpoint = aiplatform.Endpoint(endpoint_name=endpoint_resource_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Vertex AI Endpoint: {e}")

        # Build chatCompletions-style request
        prompt = self._build_prompt(patient_info, candidates)
        instances = [{
            "@requestFormat": "chatCompletions",
            "messages": [{"role": "user", "content": prompt}],
            "max_token": getattr(self, "max_output_tokens", 64000),
            "temperature": getattr(self, "temperature", 0.1),
            "top_p": 1.0,
            "top_k": -1,
        }]
        params: Dict[str, Any] = {}

        try:
            # response = self.endpoint.predict(instances=instances, parameters=params)
            client = OpenAI()
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,               
            )
            
        except Exception as e:
            raise RuntimeError(f"Prediction call failed: {e}")

        if response.output_text:
            print("====================LLM reasoning succeeded==============")
            response_text = response.output_text.strip()

            if response_text.startswith("```"):
                m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text, flags=re.IGNORECASE)
                if m:
                    response_text = m.group(1).strip()

            print(response_text)
            # model response
            output = json.loads(response_text)

            # original candidates list (whatever you passed in)
            raw_text = str(output)      # or keep the raw model text if you captured it
            truncated = False           # set True if you detected truncation

            selected_item_index = output.get("selected_item_index")
            selected_item = output.get("decision")

            return {
                "selected_item": selected_item,
                "selected_item_index": selected_item_index,
                "confidence": output.get("confidence"),
                "reasoning": output.get("why"),
                "key_factors": output.get("key_factors", []),
                "evidence_match": output.get("evidence_match", {}),
                "raw_text": raw_text,
                "truncated": truncated,
                "total_candidates": len(candidates),
            }

        else:
            return {
                "error": "LLM reasoning failed, no response",
                "selected_item": candidates[0] if candidates else None,
                "reasoning": "",
                "confidence": 0.0,
                "raw_text": ""
            }


