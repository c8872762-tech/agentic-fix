"""Vision Analyst agent: analyze photo to identify item and problem."""
from __future__ import annotations
import logging
from src.models.schemas import IssueAnalysis
from src.utils.config import load_prompt
from src.utils.llm import llm_vision_json

logger = logging.getLogger(__name__)

_DEFAULT_SYSTEM = """You are a home maintenance expert analyzing a photo. Describe exactly what you see:
1. What item is shown? (e.g., light bulb, battery, air filter, faucet, outlet cover)
2. What is wrong with it? (e.g., broken, burned out, cracked, missing, worn)
3. Read any visible text: brand names, model numbers, wattage, voltage, size markings.
4. Describe the physical characteristics: shape, color, size, base/connector type.

Rules:
- Only report what is VISIBLE. Do not guess text you cannot read.
- If the image is blurry or unclear, say so and set confidence low.
- Do not recommend products. Only describe what you see.

Return a JSON object with these exact fields:
{"item_category": "string", "problem_type": "string", "visible_brand": "string or null", "visible_model": "string or null", "visible_text": ["string"], "description": "string", "confidence": 0.0}"""


def analyze(photo_path: str, session_id: str, user_description: str = "") -> IssueAnalysis:
    """Analyze a photo and return an IssueAnalysis."""
    system = load_prompt("vision_analyst") or _DEFAULT_SYSTEM
    user_text = "Analyze this photo of a home maintenance issue."
    if user_description:
        user_text += f"\n\nUser description: {user_description}"

    try:
        result = llm_vision_json(system, user_text, photo_path)
        return IssueAnalysis(
            session_id=session_id,
            item_category=result.get("item_category", "other"),
            problem_type=result.get("problem_type", "unknown"),
            visible_brand=result.get("visible_brand"),
            visible_model=result.get("visible_model"),
            visible_text=result.get("visible_text", []),
            description=result.get("description", ""),
            confidence=float(result.get("confidence", 0.5)),
        )
    except Exception as e:
        logger.error("Vision analysis failed: %s", e)
        return IssueAnalysis(session_id=session_id, description=f"Analysis failed: {e}", confidence=0.0)
