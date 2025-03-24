import os
import requests
import json
from pathlib import Path

from models import Config, Plugin
from consts import Services, Plugins

KONG_ADDR = os.getenv("KONG_ADDR", "http://localhost:8001")
CONSUMER_USERNAME = os.getenv("CONSUMER_USERNAME", "api_user")
CREDENTIAL_KEY = os.getenv("CREDENTIAL_KEY", "issuer_key")
JWT_SECRET = os.getenv("JWT_SECRET", "jwt_secret")
LOGS_ENDPOINT = os.getenv("LOGS_ENDPOINT", "http://localhost:4318/v1/logs")
TRACES_ENDPOINT = os.getenv("TRACES_ENDPOINT", "http://localhost:4318/v1/traces")

def check_if_service_scoped_plugin_exists(plugin_name:str,service_id:str) -> tuple[bool, str]:
    """
    Checks if a service scoped plugin exists in Kong
    if it exists, returns True, plugin ID
    else, returns False, None
    """

    url = f"{KONG_ADDR}/services/{service_id}/plugins"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to check if plugin {plugin_name} exists: {response.text}")
    plugins = response.json()["data"]
    for plugin in plugins:
        if plugin["instance_name"] == plugin_name:
            return True, plugin["id"]
    return False, None


def create_service_scoped_plugin(plugin_name:str,plugin_config:dict,service_ids:list[str],plugins:list[Plugin]):
    url = f"{KONG_ADDR}/default/plugins"
    print(f"Creating {plugin_name} plugin")
    plugin_config["instance_name"] = plugin_name
    for service_id in service_ids:
        print("Service ID: ",service_id)

        exists, _id = check_if_service_scoped_plugin_exists(plugin_name,service_id)
        if exists:
            print(f"Plugin {plugin_name} already exists")
            plugins.append(Plugin(name=plugin_name,service_id=service_id,config=plugin_config,_id=_id))
            continue

        plugin_config["service"] = {
            "id": service_id
        }
        response = requests.post(url, json=plugin_config)
        if response.status_code == 201:
            print("Plugin configuration created successfully")
            plugins.append(Plugin(name=plugin_name,service_id=service_id,config=plugin_config,_id=response.json()["id"]))
        else:
            raise Exception(f"Failed to create plugin configuration: {response.text}")

def check_if_global_plugin_exists(plugin_name:str) -> tuple[bool, str]:
    """
    Checks if a global plugin exists in Kong
    if it exists, returns True, plugin ID
    else, returns False, None
    """

    url = f"{KONG_ADDR}/default/plugins"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to check if plugin {plugin_name} exists: {response.text}")
    plugins = response.json()["data"]
    for plugin in plugins:
        if plugin["route"] != None or plugin["service"] != None:
            # Skip service scoped and route scoped plugins
            continue
        if plugin["instance_name"] == plugin_name:
            return True, plugin["id"]
    return False, None

def create_global_plugin(plugin_name:str,plugin_config:dict,plugins:list[Plugin]):
    url = f"{KONG_ADDR}/default/plugins"
    print(f"Creating {plugin_name} plugin")
    plugin_config["instance_name"] = plugin_name
    exists, _id = check_if_global_plugin_exists(plugin_name)
    if exists:
        print(f"Plugin {plugin_name} already exists")
        plugins.append(Plugin(name=plugin_name,config=plugin_config,_id=_id))
        return
    response = requests.post(url, json=plugin_config)
    if response.status_code == 201:
        print("Plugin configuration created successfully")
        plugins.append(Plugin(name=plugin_name,config=plugin_config,_id=response.json()["id"]))
    else:
        raise Exception(f"Failed to create plugin configuration: {response.text}")

def install_plugins(config:Config) -> list[Plugin]:
    plugins:list[Plugin] = []

    service_names_to_install_jwt_plugins_for = [Services.MONITOR]
    service_ids_to_install_jwt_plugins_for = [config.get_service_id_by_name(service_name) for service_name in service_names_to_install_jwt_plugins_for]

    setup_jwt_plugin(service_ids_to_install_jwt_plugins_for, plugins)

    # Install jwt-claim-to-header plugin
    lua_script = Path("tasks/plugins/access.lua").read_text()
    plugin_config = json.loads(Path("tasks/plugins/jwt_claim_to_header.json").read_text())
    plugin_config["config"]["access"] = [lua_script]
    create_service_scoped_plugin(Plugins.JWT_CLAIM_TO_HEADER,plugin_config,service_ids_to_install_jwt_plugins_for, plugins)

    # Install Open Telemetery plugin
    plugin_config = json.loads(Path("tasks/plugins/opentelemetry.json").read_text())
    ## Update traces and logs endpoint
    plugin_config["config"]["traces_endpoint"] = TRACES_ENDPOINT
    plugin_config["config"]["logs_endpoint"] = LOGS_ENDPOINT

    create_global_plugin(Plugins.OPEN_TELEMETRY,plugin_config, plugins)

    # Install Prometheus plugin
    plugin_config = json.loads(Path("tasks/plugins/prometheus.json").read_text())
    create_global_plugin(Plugins.PROMETHEUS, plugin_config, plugins)

    print("Plugins installed successfully\n")

    return plugins


def setup_jwt_plugin(service_ids_to_install_jwt_plugins_for:list[str], plugins: list[Plugin]):
    # Install JWT plugin
    jwt_plugin_config = json.loads(Path("tasks/plugins/jwt.json").read_text())
    create_service_scoped_plugin(Plugins.JWT,jwt_plugin_config,service_ids_to_install_jwt_plugins_for, plugins)

    # Create a consumer

    ## Check if consumer exists
    url = f"{KONG_ADDR}/consumers/{CONSUMER_USERNAME}"
    response = requests.get(url)
    if response.status_code == 404:
        ## Create consumer
        url = f"{KONG_ADDR}/consumers/"
        create_consumer_response = requests.post(url, json={"username": CONSUMER_USERNAME})
        if create_consumer_response.status_code != 201:
            raise Exception(f"Failed to create consumer: {create_consumer_response.text}")
        print("Consumer created successfully")

    if response.status_code not in [200, 404]:
        raise Exception(f"Failed to check if consumer exists: {response.text}")

    # Create JWT credential
    url = f"{KONG_ADDR}/consumers/{CONSUMER_USERNAME}/jwt"

    ## Check if credential exists
    response = requests.get(url)
    credentials = response.json()["data"]
    if len(credentials) > 0:
        print("JWT credential already exists")
        return

    ## Create credential
    response = requests.post(url, json={"key": CREDENTIAL_KEY,"secret": JWT_SECRET})    
    if response.status_code == 201:
        print("JWT credential created successfully")
    else:
        raise Exception(f"Failed to create JWT credential: {response.text}")

