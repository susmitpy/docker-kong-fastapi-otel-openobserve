import json
from pathlib import Path
from typing import Optional
import requests
import os
from models import UpStream
from consts import UpStreams

KONG_ADDR = os.getenv("KONG_ADDR", "http://localhost:8001")

def check_if_upstream_exists(name:str) -> tuple[bool, Optional[str]]:
    """
    Checks if an upstream exists in Kong
    if it exists, returns True, Upstream ID
    else, returns False, None
    """

    url = f"{KONG_ADDR}/upstreams/{name}"
    response = requests.get(url)
    if response.status_code == 200:
        return True, response.json()["id"]
    elif response.status_code == 404:
        return False, None
    else:
        raise Exception(f"Failed to check if upstream {name} exists: {response.text}")

def create_upstreams() -> list[UpStream]:
    url = f"{KONG_ADDR}/upstreams"
    upstreams = [UpStream(name=UpStreams.AUTH), UpStream(name=UpStreams.MONITOR)]

    for upstream in upstreams:
        exists, _id = check_if_upstream_exists(upstream.name)
        if exists:
            upstream._id = _id
            print(f"Upstream {upstream} already exists")
            continue
        config = json.loads(Path("tasks/upstreams/config.json").read_text())
        config["name"] = upstream.name
        response = requests.post(url, json=config)
        if response.status_code == 201:
            upstream._id = response.json()["id"]
            print(f"Upstream {upstream} created successfully")
        else:
            print(f"Failed to create upstream {upstream}: {response.text}")
        
    print("Upstreams created successfully\n")
    return upstreams