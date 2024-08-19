import streamlit as st
import requests
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# IBM Watsonx.ai text generation API details
api_key = "jUGpPn1TSS6KkLC_L7J4S_s6k4vh2xt96SDJUL-tu-lv"
url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
project_id = "3d6f1050-fa3f-4017-87d1-767f18a4a7fd"
model_id = "meta-llama/llama-3-405b-instruct"

def get_access_token(api_key):
    auth_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }

    response = requests.post(auth_url, headers=headers, data=data)

    if response.status_code != 200:
        st.error("Failed to get access token: " + str(response.text))
        raise Exception("Failed to get access token: " + str(response.text))

    token_info = response.json()
    return token_info['access_token']

access_token = get_access_token(api_key)

def get_watson_response(prompt, access_token):
    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 300,  # Adjusted token limit for concise responses
            "repetition_penalty": 1
        },
        "model_id": model_id,
        "project_id": project_id
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        st.error("Non-200 response: " + str(response.text))
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    response_text = data['results'][0]['generated_text'].strip()
    return response_text

st.title('Marketing Email Generator - SBA Info Solutions')

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

with st.form(key='email_form'):
    st.header('Enter the details for the marketing email:')
    
    product_name = st.text_input("Product Name")
    target_audience = st.text_input("Target Audience")
    main_features = st.text_area("Main Features (comma-separated)")
    offer_details = st.text_area("Offer Details")
    call_to_action = st.text_input("Call to Action")

    submit_button = st.form_submit_button(label='Generate Email')

if submit_button:
    if all([product_name, target_audience, main_features, offer_details, call_to_action]):
        user_input = f"""
        Generate a marketing email with the following details:
        Product Name: {product_name}
        Target Audience: {target_audience}
        Main Features: {main_features}
        Offer Details: {offer_details}
        Call to Action: {call_to_action}
        """
        st.session_state.chat_history.append(f"User Input: {user_input.strip()}")

        response = get_watson_response(user_input.strip(), access_token)
        
        # Generate email subject based on the product name and main features
        email_subject = f"Introducing {product_name} - {main_features.split(',')[0]}!"

        st.session_state.chat_history.append(f"Generated Email:\n\nSubject: {email_subject}\n\n{response}")

if st.session_state.chat_history:
    for message in st.session_state.chat_history:
        st.write(message)
