import requests
import os
from models import Config, Route
from consts import Services, Routes

KONG_ADDR = os.getenv("KONG_ADDR", "http://localhost:8001")

def check_if_route_exists(name:str) -> tuple[bool, str]:
    """
    Checks if a route exists in Kong
    if it exists, returns True, route ID
    else, returns False, None
    """

    url = f"{KONG_ADDR}/routes/{name}"
    response = requests.get(url)
    if response.status_code == 200:
        return True, response.json()["id"]
    elif response.status_code == 404:
        return False, None
    else:
        raise Exception(f"Failed to check if route {name} exists: {response.text}")

def create_routes(config:Config) -> list[Route]:
    url = f"{KONG_ADDR}/routes"
    routes = [
        Route(name=Routes.AUTH, service_id=config.get_service_id_by_name(Services.AUTH), path="/api/auth"),
        Route(name=Routes.MONITOR, service_id=config.get_service_id_by_name(Services.MONITOR), path="/api/monitor")
    ]

    for route in routes:
        exists, _id = check_if_route_exists(route.name)
        if exists:
            route._id = _id
            print(f"Route {route} already exists")
            continue
        response = requests.post(url, json={"name": route.name, "paths":[route.path], "service": {"id": route.service_id}})
        if response.status_code == 201:
            route._id = response.json()["id"]
            print(f"Route {route} created successfully")
        else:
            print(f"Failed to create route {route}: {response.text}")
        
    print("Routes created successfully\n")
    return routes
    