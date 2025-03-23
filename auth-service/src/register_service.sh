#!/bin/bash

echo "[DEBUG] Starting service registration script"

UPSTREAM_NAME=$1
UPSTREAM_PORT=$2
SUBNET_PREFIX=$3  # New argument for subnet prefix (e.g., "172.28.4")

echo "[DEBUG] Input parameters: UPSTREAM_NAME=$UPSTREAM_NAME, UPSTREAM_PORT=$UPSTREAM_PORT, SUBNET_PREFIX=$SUBNET_PREFIX"

# Get all IP addresses
HOST_IPS=$(hostname -i)
echo "[DEBUG] All Host IP addresses: $HOST_IPS"

# Select the IP from the specified subnet if provided
if [[ -n "$SUBNET_PREFIX" ]]; then
    # Escape dots for grep
    SUBNET_PATTERN=$(echo $SUBNET_PREFIX | sed 's/\./\\./g')
    # Match the provided subnet pattern
    HOST_IP=$(echo $HOST_IPS | grep -o "$SUBNET_PATTERN\.[0-9]*" || echo $HOST_IPS | awk '{print $1}')
else
    # If no subnet specified, just use the first IP
    HOST_IP=$(echo $HOST_IPS | awk '{print $1}')
fi

echo "[DEBUG] Selected IP address: $HOST_IP"

echo "[DEBUG] Attempting to register service with Kong at http://kong:8001"

# Register the service in Kong API Gateway
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://kong:8001/upstreams/$UPSTREAM_NAME/targets --data "target=$HOST_IP:$UPSTREAM_PORT")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

echo "[DEBUG] Kong API response code: $HTTP_CODE"
echo "[DEBUG] Kong API response body: $RESPONSE_BODY"

# Consider both 2xx responses and 409 (Conflict) as success
if [[ ($HTTP_CODE -ge 200 && $HTTP_CODE -lt 300) || $HTTP_CODE -eq 409 ]]; then
    if [[ $HTTP_CODE -eq 409 ]]; then
        echo "[DEBUG] Service already registered (409 Conflict) - continuing as success"
    else
        echo "[DEBUG] Service registration successful"
    fi
    exit 0
else
    echo "[DEBUG] Service registration failed"
    exit 1
fi