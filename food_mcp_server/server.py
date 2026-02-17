from mcp.server.fastmcp import FastMCP

mcp = FastMCP("food_server")

@mcp.tool()
def search_recipe(ingredients: list[str]) -> dict:
    """
    Search recipe database based on available ingredients.
    """

    mock_db = {
        "thai_omelette_rice": {
            "ingredients": ["egg", "rice"],
            "calories": 450
        },
        "pork_soy_rice": {
            "ingredients": ["pork", "soy sauce", "rice"],
            "calories": 550
        }
    }

    for name, data in mock_db.items():
        if all(i in ingredients for i in data["ingredients"]):
            return {
                "dish_name": name,
                "calories": data["calories"]
            }

    return {
        "dish_name": "Creative Fusion Dish",
        "calories": 500
    }


if __name__ == "__main__":
    mcp.run()
