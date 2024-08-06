import streamlit as st
import requests
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# IBM Watsonx.ai text generation API details
api_key = "_OtWEUKuRFovnjErgp0BQSh8sgSzJ8f_H63ZLGC43ayF"  # Updated API key
url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
project_id = "06a95679-80d6-4cd6-949f-015ccf509441"  # Updated project ID
model_id = "meta-llama/llama-3-405b-instruct"  # Updated model ID

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
            "max_new_tokens": 900,
            "min_new_tokens": 0,
            "stop_sequences": [],
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

st.write("""
**Requirement Text:**
Please provide the following details for generating a marketing email:
- Product or service name
- Target audience
- Key benefits or features
- Call to action (e.g., visit our website, sign up now, etc.)
- Any additional information or special offers
""")

user_input = st.text_area("Enter the details for the marketing email:")

if st.button("Generate Email"):
    if user_input:
        st.session_state.chat_history.append(f"User Input: {user_input}")
        
        response = get_watson_response(user_input, access_token)
        st.session_state.chat_history.append(f"Generated Email: {response}")

if st.session_state.chat_history:
    for message in st.session_state.chat_history:
        st.write(message)
