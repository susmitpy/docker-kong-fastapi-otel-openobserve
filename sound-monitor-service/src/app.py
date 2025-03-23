from fastapi import FastAPI, Request, Response
from fastapi import status
from create_app import create_app
from time import sleep
from obs_utils import set_request_attributes

app = FastAPI()
app, tracer, logger = create_app("sound-service")

@app.get("/alerts")
@tracer.start_as_current_span(name="alerts")
@set_request_attributes
async def alerts(request: Request):
    logger.info("Fetching alerts")
    with tracer.start_span("fetch_alerts") as fetch_alerts_span:
        sleep(1)
        alerts = [{"id": 1, "name": "Alert 1"}, {"id": 2, "name": "Alert 2"}]
        fetch_alerts_span.add_event("Fetched Alerts", attributes={"num_alerts": len(alerts)})
    sleep(1)
    return {"alerts": alerts}


@app.get("/health")
async def health():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

