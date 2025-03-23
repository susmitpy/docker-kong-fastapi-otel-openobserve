from fastapi import  Request, Response
from fastapi import status
from pydantic import BaseModel
import jwt
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta, timezone
import os
from create_app import create_app

app, tracer, logger = create_app("auth-service")


SECRET = os.environ.get("JWT_SECRET", "jwt_secret")
issuer = os.environ.get("CREDENTIAL_KEY", "issuer_key")

class User(BaseModel):
    username: str
    password: str

users_db = {"susmit": "susmit"}

@app.post("/login")
async def login(user: User):
    logger.info(f"login request for user: {user.username}")
    if users_db.get(user.username) == user.password:
        token = jwt.encode(
            {
                "iss": issuer,
                "sub": user.username,
                "exp": datetime.now(timezone.utc) + timedelta(hours=3)
            },
            SECRET,
            algorithm="HS256"
        )

        return {"access_token": token}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/health")
async def health(request: Request):
    return Response(status_code=status.HTTP_204_NO_CONTENT)