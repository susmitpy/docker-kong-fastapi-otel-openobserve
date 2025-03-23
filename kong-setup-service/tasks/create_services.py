from typing import Optional
import requests
import os

from models import Service
from consts import UpStreams, Services

KONG_ADDR = os.getenv("KONG_ADDR", "http://localhost:8001")

def check_if_service_exists(name:str) -> tuple[bool, Optional[str]]:
    """
    Checks if an service exists in Kong
    if it exists, returns True, service ID
    else, returns False, None
    """

    url = f"{KONG_ADDR}/services/{name}"
    response = requests.get(url)
    if response.status_code == 200:
        return True, response.json()["id"]
    elif response.status_code == 404:
        return False, None
    else:
        raise Exception(f"Failed to check if service {name} exists: {response.text}")

def create_services() -> list[Service]:
    url = f"{KONG_ADDR}/services"
    services = [
        Service(name=Services.AUTH, upstream=UpStreams.AUTH),
        Service(name=Services.MONITOR, upstream=UpStreams.MONITOR)
    ]
    for service in services:
        exists, _id = check_if_service_exists(service.name)
        if exists:
            service._id = _id
            print(f"Service {service} already exists")
            continue
        response = requests.post(url, json={"name": service.name, "host": service.upstream})
        if response.status_code == 201:
            service._id = response.json()["id"]
            print(f"Service {service} created successfully")
        else:
            print(f"Failed to create service {service}: {response.text}")
        
    print("Services created successfully\n")
    return services
    