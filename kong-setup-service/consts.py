class UpStreams:
    AUTH = "auth-upstream"
    MONITOR = "sound-monitor-upstream"

class Services:
    AUTH = "auth-service"
    MONITOR = "sound-monitor-service"

class Routes:
    AUTH = "auth-route"
    MONITOR = "sound-monitor-route"

class Plugins:
    JWT = "jwt"
    JWT_CLAIM_TO_HEADER = "jwt-claim-to-header"
    OPEN_TELEMETRY = "opentelemetry"
    PROMETHEUS = "prometheus"