import os
from fastapi import FastAPI, Response, status

app = FastAPI()

APP_ENV = os.getenv("APP_ENV", "local")
MESSAGE = os.getenv("MESSAGE", "Hello from my-api")
SECRET_MESSAGE = os.getenv("SECRET_MESSAGE", "secret-not-set")

# readiness 테스트용 플래그
APP_READY = os.getenv("APP_READY", "true").lower() == "true"

@app.get("/")
def root():
    return {
        "service": "my-api",
        "message": MESSAGE,
        "env": APP_ENV,
    }


@app.get("/healthz/live")
def liveness():
    return {
        "status": "alive"
    }


@app.get("/healthz/ready")
def readiness(response: Response):
    if not APP_READY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not ready",
            "reason": "APP_READY is false"
        }

    if SECRET_MESSAGE == "secret-not-set":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not ready",
            "reason": "SECRET_MESSAGE is not loaded"
        }

    return {
        "status": "ready"
    }


@app.get("/config")
def config():
    return {
        "env": APP_ENV,
        "message": MESSAGE,
        "secretLoaded": SECRET_MESSAGE != "secret-not-set",
        "appReady": APP_READY
    }

@app.get("/version")
def version():
    return {
        "version": "v2",
        "deployment": "argocd-gitops"
    }