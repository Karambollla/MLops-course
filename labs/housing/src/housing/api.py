"""Готовая HTTP-обвязка; модель и её обучение реализует учащийся."""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from housing.features import FEATURES


class Instance(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    MedInc: FiniteFloat
    HouseAge: FiniteFloat
    AveRooms: FiniteFloat
    AveBedrms: FiniteFloat
    Population: FiniteFloat
    AveOccup: FiniteFloat
    Latitude: FiniteFloat
    Longitude: FiniteFloat


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    instances: list[Instance] = Field(min_length=1, max_length=256)


def create_app(model_path: Path | None = None) -> FastAPI:
    artifact = model_path or Path(os.getenv("MODEL_PATH", "work/artifacts/model.joblib"))
    registry = CollectorRegistry()
    requests = Counter("http_requests_total", "HTTP responses", ["route", "status"], registry=registry)
    latency = Histogram("http_request_duration_seconds", "HTTP latency", ["route"], registry=registry)

    @asynccontextmanager
    async def lifespan(app):
        app.state.bundle = None
        if artifact.exists():
            bundle = joblib.load(artifact)  # Load only your own trusted artifacts.
            if (not isinstance(bundle, dict) or bundle.get("schema_version") != 1
                    or bundle.get("features") != FEATURES or not bundle.get("model_version")
                    or not hasattr(bundle.get("pipeline"), "predict")):
                raise RuntimeError("Несовместимый bundle: проверь schema_version, features, pipeline и model_version")
            app.state.bundle = bundle
        yield

    app = FastAPI(title="Housing course starter", lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        # Do not echo raw input: it may contain nonfinite numbers or sensitive values.
        detail = [{"type": error["type"], "loc": error["loc"], "msg": error["msg"]}
                  for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": detail})

    @app.middleware("http")
    async def instrument(request, call_next):
        started = perf_counter()
        status = "500"
        try:
            response = await call_next(request)
            status = str(response.status_code)
            return response
        finally:
            route = getattr(request.scope.get("route"), "path", "unknown")
            requests.labels(route, status).inc()
            latency.labels(route).observe(perf_counter() - started)

    @app.get("/live")
    def live():
        return {"status": "alive"}

    @app.get("/ready")
    def ready():
        if app.state.bundle is None:
            raise HTTPException(503, "Модель ещё не обучена или MODEL_PATH не найден")
        return {"status": "ready", "model_version": app.state.bundle["model_version"]}

    @app.post("/predict")
    def predict(body: PredictionRequest):
        if app.state.bundle is None:
            raise HTTPException(503, "Модель не загружена")
        frame = pd.DataFrame([row.model_dump() for row in body.instances], columns=FEATURES)
        values = app.state.bundle["pipeline"].predict(frame)
        return {"predictions": [float(value) for value in values],
                "model_version": app.state.bundle["model_version"], "target_unit": "100000 USD"}

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(registry), headers={"Content-Type": CONTENT_TYPE_LATEST})

    return app


app = create_app()
