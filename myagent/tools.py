# path: myagent/tools.py

import os
import json
import requests
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONFIG
# =========================

SPOON_URL = "https://api.spoonacular.com/recipes/findByIngredients"
CACHE_FILE = Path(__file__).parent / "translation_cache.json"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SPOON_KEY = os.getenv("SPOONACULAR_API_KEY")

# =========================
# BASE MAP (Fast + Free)
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "ingredient_map.json"), "r", encoding="utf-8") as f:
    BASE_MAP = json.load(f)

# =========================
# CACHE SYSTEM
# =========================

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# =========================
# LANGUAGE DETECT (Fast)
# =========================

def detect_language(text: str) -> str:
    if any("\u0E00" <= c <= "\u0E7F" for c in text):
        return "th"
    if any("\u3040" <= c <= "\u30FF" for c in text):
        return "ja"
    return "en"

# =========================
# LLM Batch Translate
# =========================

def batch_translate(words: List[str], target_lang: str) -> List[str]:
    if not GOOGLE_API_KEY:
        return words

    cache = load_cache()
    translated = []
    missing = []

    # เช็ค cache ก่อน
    for w in words:
        key = f"{w}_{target_lang}"
        if key in cache:
            translated.append(cache[key])
        else:
            translated.append(None)
            missing.append(w)

    # ถ้ามีคำที่ยังไม่แปล
    if missing:
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
            Translate the following words to {target_lang}.
            Return ONLY comma-separated words in same order.
            Words:
            {", ".join(missing)}
            """

            response = model.generate_content(prompt)
            results = [w.strip() for w in response.text.split(",")]

            # update cache
            for original, new_word in zip(missing, results):
                cache[f"{original}_{target_lang}"] = new_word

            save_cache(cache)

        except Exception:
            return words

        # ใส่ค่าที่แปลกลับเข้า list
        i = 0
        for idx in range(len(translated)):
            if translated[idx] is None:
                translated[idx] = results[i]
                i += 1

    return translated

# =========================
# SPOONACULAR CALL
# =========================

def call_spoon_api(ingredients_eng: List[str]) -> List[dict]:
    if not SPOON_KEY:
        return []

    params = {
        "ingredients": ",".join(ingredients_eng),
        "number": 5,
        "ranking": 1,
        "ignorePantry": False,
        "apiKey": SPOON_KEY,
    }

    response = requests.get(SPOON_URL, params=params)
    if response.status_code != 200:
        return []

    return response.json()

# =========================
# MAIN SEARCH FUNCTION
# =========================

def search_recipe(ingredients: List[str]) -> dict:
    if not ingredients:
        return {"error": "No ingredients provided"}

    original_lang = detect_language(" ".join(ingredients))

    # STEP 1: Convert to English
    if original_lang in BASE_MAP:
        mapped = []
        for word in ingredients:
            mapped.append(BASE_MAP[original_lang].get(word, word))
        ingredients_eng = batch_translate(mapped, "English")
    elif original_lang != "en":
        ingredients_eng = batch_translate(ingredients, "English")
    else:
        ingredients_eng = ingredients

    # STEP 2: Call Spoonacular
    results = call_spoon_api(ingredients_eng)

    if not results:
        return {"message": "No recipes found"}

    # STEP 3: Translate output back
    if original_lang != "en":
        titles = [r["title"] for r in results]
        translated_titles = batch_translate(titles, original_lang)

        for r, new_title in zip(results, translated_titles):
            r["title"] = new_title

    return {
        "language": original_lang,
        "ingredients_used": ingredients,
        "recipes": [
            {
                "title": r["title"],
                "usedIngredientCount": r.get("usedIngredientCount"),
                "missedIngredientCount": r.get("missedIngredientCount"),
            }
            for r in results
        ],
    }