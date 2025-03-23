from dataclasses import dataclass, field
from typing import Optional

@dataclass
class UpStream:
    name: str
    _id: Optional[str] = None

@dataclass
class Service:
    name: str
    upstream: str
    _id: Optional[str] = None

@dataclass
class Route:
    name: str
    service_id: str
    path: str
    _id: Optional[str] = None

@dataclass  
class Plugin:
    name: str
    config: dict
    service_id: Optional[str] = None
    _id: Optional[str] = None

@dataclass
class Config:
    upstreams: list[UpStream] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    routes: list[Route] = field(default_factory=list)
    plugins: list[Plugin] = field(default_factory=list)

    def get_service_id_by_name(self, service_name) -> Optional[str]:
        service = next((service for service in self.services if service.name == service_name), None)
        if service:
            return service._id
        return None

    def __str__(self):
        return f"""
        Kong Configuration:
        - Upstreams: {len(self.upstreams)}
        - Services: {len(self.services)}
        - Routes: {len(self.routes)}
        - Plugins: {len(self.plugins)}
        """