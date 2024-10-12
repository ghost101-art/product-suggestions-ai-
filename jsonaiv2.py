import openai
import requests
import googlemaps
import json

# Initialize API keys
openai.api_key = 'GPT KEY'  # CHANGE THESE
google_maps_api_key = 'MAP KEY'  # CHANGE THESE

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=google_maps_api_key)

# Define location and search parameters
radius = 40233  # 25 miles in meters
store_type = 'store and restaurants'

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
         "content": "You are a helpful assistant providing product suggestions based on nearby stores and price."},
        {"role": "user",
         "content": f"Suggest unique {user_interest} ideas for consumers in {location}, based on the season, culture, trends, and nearby stores: {store_list}. Only list top 3 stores or restaurants that are relevant to the item the user is interested in. Only say the top 3 stores with one item suggested or restertants (only if they ask something related to food). Don't talk anything more then it is necessary"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=300,
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

    # Save suggestions to JSON file
    with open("suggestions.json", "w") as json_file:
        json.dump({"suggestions": boston_suggestions}, json_file, indent=4)

    # Print suggestions for the user
    for i, suggestion in enumerate(boston_suggestions, start=1):
        print(f"{suggestion}")
else:
    print("Could not determine location.")

if __name__ == "__main__":
    get_product_suggestions(get_location(), get_all_nearby_stores(latitude, longitude, radius=radius), user_interest)
