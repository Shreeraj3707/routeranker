"""
/ predict endpoint — inference on new feature vectors.
"""

from fastapi import APIRouter, HTTPException
from backend.schemas import RouteFeatures, PredictionResponse
from backend.model_loader import bundle

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("", response_model=PredictionResponse)
def predict(features: RouteFeatures):
    if not bundle._loaded:
        try:
            bundle.load()
        except FileNotFoundError as e:
            raise HTTPException(500, f"Models missing: {e}")

    try:
        performance, cluster, suggestions = bundle.predict(features.dict())
    except Exception as e:
        raise HTTPException(400, f"Inference failed: {e}")

    return PredictionResponse(
        route_id=None,
        performance=performance,
        cluster=cluster,
        suggestions=suggestions,
    )