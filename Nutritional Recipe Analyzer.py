import requests
import pandas as pd
import streamlit as st

# Replace with your own API Key from USDA FoodData Central
API_KEY = 'your API key'

#For getting API Key Login at : https://www.ers.usda.gov/developer/data-apis/#apiForm
# After logging in the API will be sent to the registered email


# Function to get nutritional information for a given food item
def get_nutritional_info(food_name):
    base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        'api_key': API_KEY,
        'query': food_name,
        'pageSize': 1  
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()

        if 'foods' in data and len(data['foods']) > 0:
            food_data = data['foods'][0]
            nutrients = {nutrient['nutrientName']: nutrient['value'] for nutrient in food_data['foodNutrients']}
            return nutrients
        else:
            return {}
    else:
        return {}


# Function to analyze the nutrient content of a recipe
def analyze_recipe(ingredients):
    total_nutrients = {}

    for ingredient, quantity in ingredients.items():
        nutrient_info = get_nutritional_info(ingredient)

        if nutrient_info:
            for nutrient, value in nutrient_info.items():
                # Assuming quantity is in grams, adjust nutrient calculation
                if nutrient in total_nutrients:
                    total_nutrients[nutrient] += value * (quantity / 100)  # Scale by the quantity
                else:
                    total_nutrients[nutrient] = value * (quantity / 100)

    return total_nutrients


# Streamlit app
def main():
    st.title("Nutritional Recipe Analyzer")

    # Store ingredients in a session state to persist data
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = {}

    # Input form for food item and quantity
    food_item = st.text_input("Enter the food item")
    quantity = st.number_input("Enter the quantity (grams)", min_value=0.0, step=1.0)

    # "Add More" button to add food items
    if st.button("Add More"):
        if food_item and quantity > 0:
            st.session_state.ingredients[food_item] = quantity
            st.success(f"Added {quantity}g of {food_item}")
        else:
            st.warning("Please enter both a valid food item and quantity.")

    # Display the list of ingredients
    if st.session_state.ingredients:
        st.subheader("Ingredients added:")
        for food, qty in st.session_state.ingredients.items():
            st.write(f"{food}: {qty} grams")

    # "Calculate" button to compute nutritional values
    if st.button("Calculate"):
        if st.session_state.ingredients:
            nutritional_values = analyze_recipe(st.session_state.ingredients)
            if nutritional_values:
                st.subheader("Nutritional Content of the Recipe:")
                nutrients_df = pd.DataFrame(nutritional_values.items(), columns=['Nutrient', 'Value'])
                st.dataframe(nutrients_df)
            else:
                st.error("No nutritional data found for the provided ingredients.")
        else:
            st.warning("Please add at least one ingredient before calculating.")

    # Clear button to reset the input
    if st.button("Clear"):
        st.session_state.ingredients = {}
        st.success("Ingredients cleared.")


if __name__ == "__main__":
    main()
