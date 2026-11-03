"""
LLM Adapters
Optional Groq and OpenAI API integration with strict citation prompts and JSON structured output.
Automatically falls back to deterministic generation if keys are absent or requests fail.
"""
import os
import json
import httpx
from typing import Optional, Dict, Any

from backend.app.answer_generation.schema import GroundedAnswer, EvidenceCitation, AbstentionCategory
from backend.app.retrieval.models import HybridRetrievalResult
from backend.app.answer_generation.citation_validator import CitationValidator

SYSTEM_PROMPT = """You are the Aegis Industrial AI Documentation Assistant.
Your task is to answer technical questions about the Aegis Series-7 Hydraulic Control System (HCS) STRICTLY grounded in the provided evidence.

CRITICAL CONSTRAINTS:
1. ONLY make claims that are explicitly supported by the provided evidence excerpts.
2. DO NOT fabricate or guess missing technical metrics, operating temperatures, approver names, or reliability figures.
3. If an engineering parameter is not present in the evidence, set abstention_category to "GENUINELY_ABSENT" and state that evidence is insufficient.
4. If a question assumes a component that does not exist in the diagram (e.g., voltage sensor on drawing AEG-DWG-E02), set abstention_category to "FALSE_PREMISE".
5. If a document signature is blank, DO NOT invent an approver; set abstention_category to "OMITTED_COMPANION_DOCUMENT".
6. If electrical documentation documents 480V incoming but 400V compatibility is not mentioned, DO NOT claim it is incompatible; state that 400V operation is unstated (set abstention_category to "PARTIALLY_VERIFIED").
7. Output valid JSON matching the GroundedAnswer schema.
"""

class LLMAdapter:
    @classmethod
    def can_run(cls) -> bool:
        return bool(os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY"))

    @classmethod
    def generate_with_llm(
        cls,
        retrieval: HybridRetrievalResult,
        timeout_seconds: float = 15.0
    ) -> Optional[GroundedAnswer]:
        """Attempts to generate grounded answer via Groq or OpenAI; returns None on failure."""
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not groq_key and not openai_key:
            return None

        # Build context from top retrieved chunks
        evidence_text = "\n\n".join([
            f"[Chunk ID: {fc.chunk.chunk_id} | Document: {fc.chunk.filename} | Page: {fc.chunk.page_number} | Tier: {fc.chunk.trust_tier}]\n{fc.chunk.text}"
            for fc in retrieval.chunks[:7]
        ])

        user_content = f"Question: {retrieval.query}\nTarget Revision: {retrieval.target_revision or 'Current'}\n\nEvidence Excerpts:\n{evidence_text}"

        try:
            if groq_key:
                return cls._call_groq(groq_key, user_content, retrieval, timeout_seconds)
            elif openai_key:
                return cls._call_openai(openai_key, user_content, retrieval, timeout_seconds)
        except Exception:
            return None

        return None

    @classmethod
    def _call_groq(cls, api_key: str, user_content: str, retrieval: HybridRetrievalResult, timeout: float) -> Optional[GroundedAnswer]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0
        }
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content_str = data["choices"][0]["message"]["content"]
                parsed = json.loads(content_str)
                parsed["generation_method"] = "groq_llm"
                ans = GroundedAnswer(**parsed)
                # Audit validate citations
                is_valid, _, _ = CitationValidator.validate_answer_citations(ans, retrieval)
                return ans if is_valid else None
        return None

    @classmethod
    def _call_openai(cls, api_key: str, user_content: str, retrieval: HybridRetrievalResult, timeout: float) -> Optional[GroundedAnswer]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0
        }
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content_str = data["choices"][0]["message"]["content"]
                parsed = json.loads(content_str)
                parsed["generation_method"] = "openai_llm"
                ans = GroundedAnswer(**parsed)
                is_valid, _, _ = CitationValidator.validate_answer_citations(ans, retrieval)
                return ans if is_valid else None
        return None

