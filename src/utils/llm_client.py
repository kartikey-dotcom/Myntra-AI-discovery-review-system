"""
Universal LLM Client for Myntra VoC Discovery & Growth Intelligence Engine.
Supports Google Gemini and OpenAI with zero-dependency direct HTTP REST fallbacks.
Gracefully handles unconfigured/throttled keys with deterministic local AI fallbacks.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LLMClient")

class LLMClient:
    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        # Resolve Streamlit secrets if available
        st_secrets = {}
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                st_secrets = st.secrets
        except Exception:
            pass

        self.provider = (
            provider
            or st_secrets.get("LLM_PROVIDER")
            or os.getenv("LLM_PROVIDER", "gemini")
        ).lower()

        if api_key:
            self.api_key = api_key
        elif self.provider == "gemini":
            self.api_key = (
                st_secrets.get("GEMINI_API_KEY")
                or os.getenv("GEMINI_API_KEY")
            )
        else:
            self.api_key = (
                st_secrets.get("OPENAI_API_KEY")
                or os.getenv("OPENAI_API_KEY")
            )

        if self.provider == "gemini":
            self.model_name = (
                model_name
                or st_secrets.get("LLM_MODEL_NAME")
                or os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash")
            )
        else:
            self.model_name = (
                model_name
                or st_secrets.get("LLM_MODEL_NAME")
                or os.getenv("LLM_MODEL_NAME", "gpt-4o-mini")
            )

        temp_val = st_secrets.get("LLM_TEMPERATURE") or os.getenv("LLM_TEMPERATURE", "0.2")
        self.temperature = float(temp_val)

    def is_configured(self) -> bool:
        """Returns True if a valid API key is present."""
        return bool(self.api_key and len(self.api_key.strip()) > 8 and "your_" not in self.api_key)

    def test_connection(self, key_to_test: Optional[str] = None, provider: Optional[str] = None) -> Dict[str, Any]:
        """Tests live API key connection with a lightweight prompt."""
        key = key_to_test or self.api_key
        prov = (provider or self.provider).lower()

        if not key or len(key.strip()) < 8:
            return {
                "success": False,
                "error": "API Key is empty or invalid. Please configure your GEMINI_API_KEY or OPENAI_API_KEY."
            }

        try:
            if prov == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={key}"
                payload = {
                    "contents": [{"parts": [{"text": "Reply with 'CONNECTED: Myntra VoC Engine Ready' in 5 words."}]}]
                }
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {"success": True, "provider": "Google Gemini", "model": self.model_name, "response": text.strip()}
                else:
                    return {"success": False, "status_code": resp.status_code, "error": resp.text}

            elif prov == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": "Reply with 'CONNECTED: Myntra VoC Engine Ready'."}],
                    "max_tokens": 20
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    return {"success": True, "provider": "OpenAI", "model": self.model_name, "response": text.strip()}
                else:
                    return {"success": False, "status_code": resp.status_code, "error": resp.text}

            else:
                return {"success": False, "error": f"Unsupported provider: {prov}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates grounded text using the active LLM with direct REST."""
        if not self.is_configured():
            logger.debug("API key not configured; using deterministic fallback.")
            return ""

        try:
            if self.provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                contents = []
                if system_instruction:
                    contents.append({"parts": [{"text": f"SYSTEM INSTRUCTION: {system_instruction}"}]})
                contents.append({"parts": [{"text": prompt}]})

                resp = requests.post(
                    url,
                    json={"contents": contents, "generationConfig": {"temperature": self.temperature}},
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    logger.warning(f"Gemini API returned {resp.status_code}: {resp.text}")

            elif self.provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                resp = requests.post(
                    url,
                    json={"model": self.model_name, "messages": messages, "temperature": self.temperature},
                    headers=headers,
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    logger.warning(f"OpenAI API returned {resp.status_code}: {resp.text}")

        except Exception as e:
            logger.warning(f"LLM generation call failed: {e}")

        return ""

    def classify_voc_record(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Uses LLM structured reasoning to classify a complex VoC record."""
        if not self.is_configured():
            return None

        system_instruction = (
            "You are a Senior Fashion Growth & VoC Classifier for Myntra India. "
            "Classify the customer review into: "
            "1. intent: [GENUINE_PURCHASE_INTENT, AESTHETIC_BOOKMARKING, SHORTLIST_COMPARISON, PRICE_SPECULATION] "
            "2. friction: [STYLING_AND_PAIRABILITY_ANXIETY, FIT_AND_SILHOUETTE_AMBIGUITY, FABRIC_AND_TACTILE_DOUBT, SOCIAL_VALIDATION_LAG, COMPARISON_PARALYSIS, OCCASION_DISCONNECT, PRICE_WAITING] "
            "3. workaround: [WHATSAPP_SHARING, YOUTUBE_TRYON_SEARCH, PINTEREST_CANVA_MOODBOARDING, BRACKETING, NONE] "
            "4. cohort: [STUDENT_GEN_Z, WORKING_PROFESSIONAL, TIER_2_ASPIRATIONAL]. "
            "Return STRICT valid JSON only with keys: intent, friction, workaround, cohort."
        )

        prompt = f"Customer Review: \"{raw_text}\""
        response = self.generate_text(prompt, system_instruction)
        
        if response:
            try:
                # Strip markdown codeblocks if returned
                clean_json = response.strip("`").replace("json\n", "").replace("JSON\n", "").strip()
                return json.loads(clean_json)
            except Exception as e:
                logger.debug(f"Could not parse LLM JSON classification: {e}")

        return None

if __name__ == "__main__":
    client = LLMClient()
    print("Is Configured:", client.is_configured())
    print("Provider:", client.provider)
    print("Model:", client.model_name)
