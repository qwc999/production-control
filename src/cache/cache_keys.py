import hashlib
import json

from src.api.v1.schemas.batch import BatchFilter


def batch_detail_key(batch_id: int) -> str:
    return f"batch_detail:{batch_id}"


def batches_list_key(filters: BatchFilter) -> str:
    filters_data = filters.model_dump(
        mode="json",
        exclude_none=True
    )
    raw_key = json.dumps(
        filters_data,
        sort_keys=True,
        ensure_ascii=False
    )

    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"batches_list:{key_hash}"
