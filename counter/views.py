from django.shortcuts import render
import os
import requests
import json

api_id = os.getenv('API_ID')
api_key = os.getenv('API_KEY')

# Nutritionix API
# Create your views here.
def home(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')
        weight = float(request.POST.get('weight', 0))
        api_url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
        headers = {
            'Content-Type': 'application/json',
            'x-app-id': api_id,
            'x-app-key': api_key,
        }
        payload = {
            'query':query
        }
        try:
            print(f"Payload: {payload}")
            print(f"Headers: {headers}")

            api_request = requests.post(api_url, headers=headers, json=payload)
            response_data = json.loads(api_request.content)
            print(api_request.content)

            if response_data.get('foods'):
                food_data = response_data['foods'][0]
                serving_weight = food_data.get('serving_weight_grams', 100)

                def per_100g(value):
                    return round((value / serving_weight) * 100, 1) if serving_weight else value
                
                calories = per_100g(food_data.get('nf_calories', 0))
                
                running_rate = 0.082 * weight
                weightlifting_rate = 0.048 * weight
                cycling_rate = 0.08 * weight
                yoga_rate = 0.032 * weight

                api = {
                    'name': food_data.get('food_name'),
                    'calories': calories,
                    'serving_size': 100,  # Standardized to 100 grams
                    'fat_total_g': per_100g(food_data.get('nf_total_fat', 0)),
                    'fat_saturated_g': per_100g(food_data.get('nf_saturated_fat', 0)),
                    'protein_g': per_100g(food_data.get('nf_protein', 0)),
                    'sodium_mg': per_100g(food_data.get('nf_sodium', 0)),
                    'potassium_mg': per_100g(food_data.get('nf_potassium', 0)),
                    'cholesterol_mg': per_100g(food_data.get('nf_cholesterol', 0)),
                    'carbohydrates_total_g': per_100g(food_data.get('nf_total_carbohydrate', 0)),
                    'fiber_g': per_100g(food_data.get('nf_dietary_fiber', 0)),
                    'sugar_g': per_100g(food_data.get('nf_sugars', 0)),
                    'running_mins': round(calories / running_rate),
                    'weightlifting_mins': round(calories / weightlifting_rate),
                    'cycling_mins': round(calories / cycling_rate),
                    'yoga_mins': round(calories / yoga_rate),
                }
            else:
                api = "No food data found."

        except Exception as e:
            api = "Oops! There was an error."
            print(e)
        return render(request, 'home.html', {'api':api})
    else:
        return render(request, 'home.html', {'query':'Enter a valid query'})