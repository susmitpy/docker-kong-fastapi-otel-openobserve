from models import Config

from tasks.create_services import create_services
from tasks.create_upstreams import create_upstreams
from tasks.create_routes import create_routes
from tasks.install_plugins import install_plugins
from tasks.wait_for_kong import wait_for_kong

print("Waiting for Kong to be ready")
wait_for_kong()
print("Setting up Kong")

config = Config()

config.upstreams = create_upstreams()
config.services = create_services()
config.routes = create_routes(config)
config.plugins = install_plugins(config)

print("Kong setup completed successfully")
print(config)

