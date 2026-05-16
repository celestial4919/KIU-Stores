import requests
import uuid

# --- YOUR DATA GOES HERE ---
# Paste your UUID from the terminal here
X_REFERENCE_ID = "e87e71be-8a0f-4554-b833-8659f32868ca" 
# Paste your Collections Primary Key here
SUB_KEY = "c390a3f5e4cb49a684c664976cf4e33c" 

url = "https://sandbox.momodeveloper.mtn.com/v1_0/apiuser"

headers = {
    "X-Reference-Id": X_REFERENCE_ID,
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": SUB_KEY
}

body = {
    "providerCallbackHost": "localhost"
}

print(f"Attempting to provision user: {X_REFERENCE_ID}...")

try:
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 201:
        print("✅ SUCCESS! API User Created (201 Created)")
    else:
        print(f"❌ FAILED. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")