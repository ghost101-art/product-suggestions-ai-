import openai
import requests
import googlemaps
import json

# Initialize API keys
openai.api_key = 'Chat GPT API KEY'  # CHANGE THESE
google_maps_api_key = 'MAPS API KEY'  # CHANGE THESE

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=google_maps_api_key)

# Define location and search parameters
radius = 40233  # 25 miles in meters
store_type = 'store and restaurants'

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
    # Here we simulate online suggestions; in a real scenario, you could call an API or use predefined sources.
    online_suggestions = [
        {"store": "Amazon", "item": f"{user_interest} - Amazon Bestsellers"},
        {"store": "eBay", "item": f"{user_interest} - Top Quality Picks"},
        {"store": "Etsy", "item": f"Handmade {user_interest}"}
    ]
    return [f"{suggestion['store']}: {suggestion['item']}" for suggestion in online_suggestions]

def get_product_suggestions(location, stores, user_interest):
    store_list = ", ".join(stores)
    messages = [
        {"role": "system",
         "content": "You are a helpful assistant providing product suggestions based on nearby stores, price, value, and quality."},
        {"role": "user",
         "content": f"Suggest unique {user_interest} ideas for consumers in {location}, based on the season, culture, trends, and nearby stores: {store_list}. Only list top 3 stores or restaurants that are relevant to the item the user is interested in. If there are relevant stores but if you can not guarantee the product is not going to be there then state we recommended online option instead and list all online options and don't bother listing the physical stores."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=300,
        n=1,
        temperature=0.7
    )

    suggestions = response['choices'][0]['message']['content'].strip().split('\n')
    if not suggestions or "no relevant stores" in suggestions[0].lower():
        # Fallback to online suggestions if no relevant stores found
        suggestions = get_online_suggestions(user_interest)
    return suggestions

user_interest = input("What type of products are you interested in? (e.g., clothing, electronics, food): ")

location = get_location()
if location:
    latitude, longitude = location
    nearby_stores = get_all_nearby_stores(latitude, longitude)
    product_suggestions = get_product_suggestions("your area", nearby_stores, user_interest)

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
            user_interest
        )
        print(product_suggestions)
