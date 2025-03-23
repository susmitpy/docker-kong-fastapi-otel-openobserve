# Setup of the local environment

## Move Common Files to respective services

SERVICES=("auth-service" "sound-monitor-service")
FILES=("register_service.sh" "obs_utils.py" "create_app.py")

for service in "${SERVICES[@]}"; do
    for file in "${FILES[@]}"; do
        cp "./common/$file" "./$service/src/"
        echo "Copied $file to $service"
    done
done

## Make register_service.sh executable
for service in "${SERVICES[@]}"; do
    chmod +x "./$service/src/register_service.sh"
    echo "Made register_service.sh executable in $service"
done