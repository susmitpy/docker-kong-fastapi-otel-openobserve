import requests
import os
import base64
import yaml
from time import sleep

addr = os.getenv("OPENOBSERVE_ADDR", "http://localhost:5080")
username: str = os.getenv("OPENOBSERVE_USERNAME", "susmit@example.com")
password: str = os.getenv("OPENOBSERVE_PASSWORD", "passComplex#123")

def wait_for_openobserve():
    # Wait for OpenObserve to start
    MAX_TRIES = 10
    try_count = 0

    url = f"{addr}/healthz"
    while True:
        if try_count > MAX_TRIES:
            print("Timeout waiting for OpenObserve to start")
            return
        try_count += 1
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("OpenObserve is up")
                return
        except Exception as e:
            print("Waiting for OpenObserve to start")
            sleep(2)
    

def update_field_names():
    # Updates trace id and span id field names
    response = requests.post(
        f'{addr}/api/default/settings',
        auth=(username, password),
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        json={
            'span_id_field_name': 'span_id',
            'trace_id_field_name': 'trace_id'
        }
    )

    if response.status_code == 200:
        print("Updated field names")
        return
    
    print("Failed to update field names")
    print(response.text)

def get_auth_bearer_token() -> str:
    response = requests.get(
        f'{addr}/api/default/passcode',
        auth=(username, password),
        headers={'accept': 'application/json'}
    )

    if response.status_code != 200:
        raise Exception("Failed to get passcode")

    data = response.json()
    passcode = data['data']['passcode']

    bas64encoded_creds = base64.b64encode(bytes(username + ":" + passcode, "utf-8")).decode("utf-8")
    return f"Basic {bas64encoded_creds}"

def update_otel_collector_config(token:str):
    # Updates otel collector config file with the bearer token    
    with open('./otel-collector-config.yml', 'r') as file:
        config = yaml.safe_load(file)
    
    print(config)
    config['exporters']['otlp/openobserve']['headers']['Authorization'] = token
    
    with open('./otel-collector-config.yml', 'w') as file:
        yaml.safe_dump(config, file)

if __name__ == "__main__":
    wait_for_openobserve()
    update_field_names()
    token = get_auth_bearer_token()
    update_otel_collector_config(token=token)
    print("OpenObserve setup completed")
