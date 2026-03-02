import os
import json
import requests

# =========================
# ENV
# =========================

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "ingredient_map.json"), "r", encoding="utf-8") as f:
    INGREDIENT_MAP = json.load(f)

# =========================
# INGREDIENT MAPPING
# =========================

def map_ingredients(text: str):
    mapped = []
    lower_text = text.lower()

    for lang_map in INGREDIENT_MAP.values():
        for k, v in lang_map.items():
            if k.lower() in lower_text:
                mapped.append(v)

    return list(set(mapped))

# =========================
# PRIMARY API SEARCH
# =========================

def search_recipe_api(ingredients):

    if not SPOONACULAR_API_KEY:
        return []

    url = "https://api.spoonacular.com/recipes/complexSearch"

    params = {
        "includeIngredients": ",".join(ingredients),
        "number": 5,
        "addRecipeInformation": True,
        "fillIngredients": True,
        "apiKey": SPOONACULAR_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()

    if not data.get("results"):
        return []

    recipes = []

    for r in data["results"]:
        steps = []
        instructions = r.get("analyzedInstructions", [])
        if instructions:
            steps = [s["step"] for s in instructions[0].get("steps", [])]

        recipes.append({
            "name": r["title"],
            "ingredients": [
                i["original"] for i in r.get("extendedIngredients", [])
            ],
            "steps": steps
        })

    return recipes

# =========================
# MAIN TOOL ENTRY
# =========================

def search_recipe(ingredients: list[str]):

    original_input = ", ".join(ingredients)

    # map ingredient
    mapped = map_ingredients(original_input)

    if not mapped:
        mapped = ingredients

    recipes = search_recipe_api(mapped)

    return recipes