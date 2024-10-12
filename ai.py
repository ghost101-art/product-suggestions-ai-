
import openai
import requests
import googlemaps

# Initialize API keys
openai.api_key = 'CHAT GPT KEY' # CHANGE THESE
google_maps_api_key = 'MAPS API KEY' # CHANGE THESE

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=google_maps_api_key)

# Define location and search parameters
radius = 40233  # 25 miles in meters
store_type = 'store'

def get_location():
    try:
        # Use IPinfo to get location based on IP
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
    # Fetch all nearby stores within the specified radius using Google Maps Places API
    places_result = gmaps.places_nearby(
        location=(lat, lng),
        radius=radius,
        type=store_type
    )

    # Extract the names of all nearby stores
    store_names = [place['name'] for place in places_result.get('results', [])]
    return store_names

def get_product_suggestions(location, stores, user_interest):
    store_list = ", ".join(stores)
    messages = [
        {"role": "system",
         "content": "You are a helpful assistant providing product suggestions based on nearby stores."},
        {"role": "user",
         "content": f"Suggest unique {user_interest} ideas for consumers in {location}, based on the season, culture, trends, and nearby stores: {store_list}. Only list stores that are relevant to the item the user is interested in."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=100,
        n=1,
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip().split('\n')

# Ask the user what kind of products they are looking for
user_interest = input("What type of products are you interested in? (e.g., clothing, electronics, food): ")

# Main program to find location, get all nearby stores, and suggest products
location = get_location()
if location:
    latitude, longitude = location
    nearby_stores = get_all_nearby_stores(latitude, longitude)  # Using the updated radius
    boston_suggestions = get_product_suggestions("your area", nearby_stores, user_interest)

    for i, suggestion in enumerate(boston_suggestions, start=1):
        print(f"Suggestion {i}: {suggestion}")
else:
    print("Could not determine location.")
