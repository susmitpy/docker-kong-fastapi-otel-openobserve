import os
from time import sleep

import requests

KONG_ADDR = os.getenv("KONG_ADDR", "http://localhost:8001")

def wait_for_kong():
    # Wait for Kong API Gateway to start
    MAX_TRIES = 10
    try_count = 0

    url = f"{KONG_ADDR}/status"
    while True:
        if try_count > MAX_TRIES:
            print("Timeout waiting for Kong API Gateway to start")
            return
        try_count += 1
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Kong API Gateway is up")
                return
        except Exception as e:
            print("Waiting for Kong API Gateway to start")
            sleep(2)