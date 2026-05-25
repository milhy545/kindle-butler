import os
import json
from typing import Dict, Optional
from google import genai

class AIClient:
    """
    Handles interactions with LLMs for metadata normalization.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-1.5-flash'
        else:
            self.client = None

    def normalize_metadata(self, raw_author: str, raw_title: str) -> Dict[str, str]:
        """
        Uses AI to normalize author and title into a standard format.
        """
        if not self.client:
            return {"author": raw_author, "title": raw_title}
            
        prompt = f"""
        Analyze the following ebook metadata and normalize it. 
        Format author as 'First Last'.
        Clean up titles from messy filename patterns (remove .azw3, .pdf extensions, etc).
        
        Raw Author: {raw_author}
        Raw Title: {raw_title}
        
        Return JSON format ONLY: {{"author": "Normalized Author", "title": "Normalized Title"}}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.strip()
            # Handle potential markdown formatting in response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            return json.loads(text)
        except Exception:
            return {"author": raw_author, "title": raw_title}

    def enhance_content(self, text: str, target_lang: str = "cs") -> str:
        """
        Enhances technical text: translates, converts lists/tables to narrative prose,
        and appends original data at the end.
        """
        if not self.client:
            return text

        system_instruction = f"""Jsi profesionální technický redaktor a překladatel.
Tvým úkolem je vylepšit technickou dokumentaci pro pohodlné čtení na E-Ink displeji (Kindle).
Cílový jazyk: {target_lang}

Pravidla:
1. Přelož text přesně do cílového jazyka (pokud už v něm není).
2. Převeď odrážky, tabulky a technické seznamy do plynulých, čtivých odstavců (narrative prose), které se čtou jako příběh.
3. Nesmíš ztratit ŽÁDNÁ technická data.
4. Na konec dokumentu přidej nadpis (např. 'Původní technická data' v cílovém jazyce) a připoj původní strukturovaná data, aby si je čtenář mohl dohledat.
5. Vrať POUZE výsledný text ve formátu Markdown. Žádné úvodní ani závěrečné fráze mimo samotný text."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=text,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3
                )
            )
            return response.text.strip()
        except Exception:
            return text
