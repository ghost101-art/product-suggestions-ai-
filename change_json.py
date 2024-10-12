import json
import os

user_data_file = "user_data.json"

def modify_user_data():
    # Load existing data if file exists, otherwise initialize default data
    if os.path.exists(user_data_file):
        with open(user_data_file, "r") as file:
            data = json.load(file)
            print(f"Current data: {data}")
    else:
        data = {"allergies": "None", "dietary_restrictions": "None"}
        print("No existing data found. Starting with defaults.")

    # Prompt user for new values
    new_allergies = input("Enter new allergies (or type 'none' if you have no allergies): ")
    new_dietary_restrictions = input("Enter new dietary restrictions (e.g., halal, kosher, vegan, vegetarian, or type 'none' if you have none): ")

    # Update data dictionary
    data["allergies"] = new_allergies
    data["dietary_restrictions"] = new_dietary_restrictions

    # Write updated data back to file
    with open(user_data_file, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Updated data: {data}")

# Example usage
modify_user_data()
