from flask import Flask, request
import requests
import random
from datetime import datetime
import base64

app = Flask(__name__)

# M-Pesa Daraja API Credentials
MPESA_CONSUMER_KEY = 'vvWJIRWpkfumAtmgUgJ14LYFpJWUpRJAF0cMMLVCg5C2VPb2'
MPESA_CONSUMER_SECRET = '8KCYnnISTTglBajECAroPkoWKeKqrBYmfYOoEfvJWCq9kFAxdksgSuyI3IDQePTK'
BUSINESS_SHORTCODE = 'your_shortcode'  # Your shortcode here
PASSKEY = 'your_passkey'  # Your passkey here
CALLBACK_URL = 'https://yourcallbackurl.com/payment'  # Your callback URL

# Function to generate M-Pesa access token
def generate_mpesa_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return response.json().get('access_token')

# Function to initiate M-Pesa payment (STK Push)
def initiate_mpesa_payment(phone_number, amount):
    token = generate_mpesa_token()
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": generate_password(),
        "Timestamp": generate_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "Mara Wins",
        "TransactionDesc": "Payment for box selection"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Function to generate password for payment (encrypted)
def generate_password():
    timestamp = generate_timestamp()
    password_str = f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}"
    return base64.b64encode(password_str.encode()).decode()

# Function to generate timestamp
def generate_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

# Weighted random reward selection function
def get_weighted_reward():
    rewards = [
        ("Ksh.10", 70),   # 70% chance
        ("Ksh.50", 20),   # 20% chance
        ("Ksh.200", 9),   # 9% chance
        ("Ksh.1000", 1)   # 1% chance
    ]
    population, weights = zip(*rewards)
    return random.choices(population, weights, k=1)[0]

@app.route('/ussd', methods=['POST'])
def ussd():
    session_id = request.form.get("sessionId")
    service_code = request.form.get("serviceCode")
    phone_number = request.form.get("phoneNumber")
    text = request.form.get("text")

    if text == "":
        response = (
            "CON Chagua Box moja upate USHINDI PAP!\n"
            "Choose a box (1-6):\n"
            "1. Box 1\n2. Box 2\n3. Box 3\n4. Box 4\n5. Box 5\n6. Box 6\n"
        )
    else:
        try:
            box_choice = int(text)
            if 1 <= box_choice <= 6:
                # Initiate Payment
                payment_response = initiate_mpesa_payment(phone_number, amount=42)
                if payment_response.get("ResponseCode") == "0":
                    reward = get_weighted_reward()
                    response = f"END Payment successful! Your reward is: {reward}."
                else:
                    response = "END Payment initiation failed. Try again."
            else:
                response = "END Invalid choice. Please select a number between 1 and 6."
        except ValueError:
            response = "END Invalid input. Please enter a valid number."

    return response, 200, {"Content-Type": "text/plain"}

if __name__ == '__main__':
    app.run(port=5000)
