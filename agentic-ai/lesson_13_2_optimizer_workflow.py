import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(
    base_url = "https://openai.vocareum.com/v1",
    api_key=os.getenv("OPENAI_API_KEY"))

MAX_RETRIES = 5

# Example user constraints
RECIPE_REQUEST = {
    "base_dish": "pasta",
    "constraints": [
        "gluten-free",
        "vegan",
        "under 500 calories per serving",
        "high protein (>15g per serving)",
        "no coconut",
        "taste must be rated 7/10 or higher"
    ]
}

class RecipeCreatorAgent:
    def run(self, recipe_request, feedback=None) -> str:
        system_prompt = "You are an innovative and highly skilled chef, renowned for creating delicious recipes that also meet specific dietary and nutritional targets. You are good at interpreting user requests and also at refining your creations based on precise feedback."
        user_prompt = f""" Create a recipe for {recipe_request} that meets the following constraints: {RECIPE_REQUEST["constraints"]} """
        print(f"\n👨‍🍳 Creating recipe with prompt:\n{user_prompt}\n")
        if feedback is None: # First attempt
            user_prompt = f"""Recipe Request: {recipe_request}
            Create an exciting, flavorful recipe... prioritize creativity and taste first."""
            print("\n👨‍🍳 Creating initial recipe (flexible interpretation)...")
            current_temperature = 1 # Higher for more creativity
        else: # Subsequent attempts with feedback
            # 🧠 Once feedback is received, become strict about rules
            system_message = """You are an expert chef specializing in creating recipes that follow strict dietary constraints.
            You must correct previous issues and follow all requirements with precision."""
            user_prompt = f"""Recipe Request: {recipe_request}
            Your previous recipe had the following issues:\n{feedback}\nPlease create a revised recipe addressing these issues."""
            print("\n🔄 Generating revised recipe based on feedback...")
            current_temperature = 0.3 # Lower for more precision
            
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=current_temperature
        )

        print(f"\n📝 Generating recipe with prompt:\n{user_prompt}\n")

        return response.choices[0].message.content        

class NutritionEvaluatorAgent:
    def evaluate(self, recipe_request, proposed_recipe) -> str:
        print("\n🔍 Evaluating recipe for nutritional content and constraints...")
        system_message = """You are a strict dietitian. Your job is to find ANY and ALL violations... Be meticulous..."""
        user_prompt = f"""Recipe Request: {recipe_request}
        Proposed Recipe:\n{proposed_recipe}
        Please evaluate this recipe against ALL the specified requirements.
        Check EACH constraint individually...
        If ALL constraints are fully satisfied, begin your response with "APPROVED: This recipe meets all requirements."
        Otherwise, list specifically which requirements are NOT met and provide detailed suggestions..."""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content

def optimize_recipe() -> None:
    current_feedback = None
    recipeCreatorAgent = RecipeCreatorAgent()
    nutritionEvaluatorAgent = NutritionEvaluatorAgent()
    for attempt in range(MAX_RETRIES):
        print(f"\n🔄 Attempt {attempt+1} of {MAX_RETRIES}")
        current_recipe_str = recipeCreatorAgent.run(RECIPE_REQUEST, current_feedback)
        print (f"Chef proposed recipe: {current_recipe_str}")
        evaluation_str = nutritionEvaluatorAgent.evaluate(current_recipe_str, RECIPE_REQUEST)
        print (f"🧐 Critic's Evaluation: {evaluation_str}")
        if "approved" in evaluation_str.lower():
            print("\n✅ Recipe meets all constraints!")
            return current_recipe_str, evaluation_str, attempt + 1            
        current_feedback = evaluation_str
    print(f"\n❌ Failed to meet all constraints after {MAX_RETRIES} attempts.")
    return current_recipe_str, evaluation_str, MAX_RETRIES    

if __name__ == "__main__":
    optimize_recipe()
        