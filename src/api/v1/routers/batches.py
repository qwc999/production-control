from fastapi import APIRouter, Depends, status, HTTPException

from src.api.v1.dependencies import get_batch_service
from src.api.v1.schemas.batch import BatchCreate, BatchResponse
from src.domain.exceptions.exceptions import BatchAlreadyExistsError
from src.domain.services.batch_service import BatchService

router = APIRouter(prefix="/batches", tags=["Batch"])


@router.post("",
             response_model=list[BatchResponse],
             status_code=status.HTTP_201_CREATED)
async def create_batches(
        items: list[BatchCreate],
        service: BatchService = Depends(get_batch_service)
):
    try:
        batches = await service.create_batches(items)
        return batches
    except BatchAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Batch already exists"
            }
        ) from e
