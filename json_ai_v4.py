import openai
import requests
import googlemaps
import json
import os

# Initialize API keys
openai.api_key = 'GPT KEY' # CHANGES THESE
google_maps_api_key = 'MAPS KEY'  # CHANGE THESE


# Initialize Google Maps Client
gmaps = googlemaps.Client(key=google_maps_api_key)

# Define location and search parameters
radius = 40233  # 25 miles in meters
store_type = 'store and restaurants'
user_data_file = "user_data.json"


def get_location():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        if "loc" in data:
            latitude, longitude = map(float, data["loc"].split(","))
            return latitude, longitude
        else:
            print("Could not retrieve location coordinates.")
            return None
    except requests.RequestException as e:
        print("Error fetching location:", e)
        return None


def get_all_nearby_stores(lat, lng, radius=radius):
    places_result = gmaps.places_nearby(
        location=(lat, lng),
        radius=radius,
        type=store_type
    )
    store_names = [place['name'] for place in places_result.get('results', [])]
    return store_names

def get_online_suggestions(user_interest):
    online_suggestions = [
        {"store": "Amazon", "item": f"{user_interest} - Amazon Bestsellers"},
        {"store": "eBay", "item": f"{user_interest} - Top Quality Picks"},
        {"store": "Etsy", "item": f"Handmade {user_interest}"}
    ]

def get_diet(user_interest, dietary_restriction):
    # Suggestions tailored based on dietary restrictions
    if dietary_restriction.lower() == "kosher":
        online_suggestions = [
            {"finder": "https://www.totallyjewishtravel.com/KosherRestaurants/", "item": f"{user_interest} - Kosher-certified items"},
        ]
    elif dietary_restriction.lower() == "halal":
        online_suggestions = [
            {"finder": "https://www.zabihah.com/", "item": f"{user_interest} - Halal-certified products"},
        ]


def get_product_suggestions(location, stores, user_interest, allergies, dietary_restrictions, ):
    diet = get_diet(user_interest, dietary_restrictions)
    online_suggestions= get_online_suggestions(user_interest)
    store_list = ", ".join(stores)

    messages = [
        {"role": "system",
         "content": "You are a helpful assistant providing product suggestions based on nearby stores, price, value, and quality."},
        {"role": "user",
         "content": f"Suggest unique {user_interest} ideas for consumers in {location}, based on the season, culture, trends, and nearby stores: {store_list}. "
                    f"The user has the following allergies: {allergies}. They follow these dietary restrictions: {dietary_restrictions}. use {diet} to verify each resterurants you look up for the user if they have any dietary restrictions"
                    f"Only list top 3 stores or restaurants that are relevant to the item the user is interested in. If there are relevant stores but you cannot guarantee the product's availability, recommend online options instead. Here are the recommended online websites for this item: {online_suggestions}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=400,
        n=1,
        temperature=0.7
    )

    suggestions = response['choices'][0]['message']['content'].strip().split('\n')
    if not suggestions or "no relevant stores" in suggestions[0].lower():
        # Fallback to online suggestions if no relevant stores found
        suggestions = online_suggestions
    return suggestions


def get_user_preferences():
    if os.path.exists(user_data_file):
        with open(user_data_file, "r") as file:
            data = json.load(file)
            if "allergies" in data and "dietary_restrictions" in data:
                print(
                    f"Loaded saved preferences: Allergies - {data['allergies']}, Dietary Restrictions - {data['dietary_restrictions']}")
                return data['allergies'], data['dietary_restrictions']

    allergies = input("Please enter your allergies (or type 'none' if you have no allergies): ")
    dietary_restrictions = input(
        "Please enter any dietary restrictions (e.g., halal, kosher, vegan, vegetarian, or type 'none' if you have none): ")

    user_data = {
        "allergies": allergies,
        "dietary_restrictions": dietary_restrictions
    }
    with open(user_data_file, "w") as file:
        json.dump(user_data, file)

    print(f"Saved preferences: Allergies - {allergies}, Dietary Restrictions - {dietary_restrictions}")
    return allergies, dietary_restrictions


# Retrieve user preferences
user_allergies, user_dietary_restrictions = get_user_preferences()

# Ask the user what kind of products they are looking for
user_interest = input("What type of products are you interested in? (e.g., clothing, electronics, food): ")

location = get_location()
if location:
    latitude, longitude = location
    nearby_stores = get_all_nearby_stores(latitude, longitude)
    product_suggestions = get_product_suggestions("your area", nearby_stores, user_interest, user_allergies, user_dietary_restrictions)

    with open("suggestions.json", "w") as json_file:
        json.dump({"suggestions": product_suggestions}, json_file, indent=4)

    for i, suggestion in enumerate(product_suggestions, start=1):
        print(f"{suggestion}")
else:
    print("Could not determine location.")

if __name__ == "__main__":
    location = get_location()
    if location:
        latitude, longitude = location
        product_suggestions = get_product_suggestions(
            "your area",
            get_all_nearby_stores(latitude, longitude, radius=radius),
            user_interest,
            user_allergies,
            user_dietary_restrictions
        )
        print(product_suggestions)
