import csv
from pathlib import Path

from src.data.models.batch import Batch


CSV_COLUMNS = [
    "id",
    "is_closed",
    "closed_at",
    "task_description",
    "work_center_id",
    "shift",
    "team",
    "batch_number",
    "batch_date",
    "nomenclature",
    "ekn_code",
    "shift_start",
    "shift_end",
    "created_at",
    "updated_at",
]


def generate_batches_csv_export(
        batches: list[Batch],
        file_path: Path,
) -> None:
    with file_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for batch in batches:
            writer.writerow({
                "id": batch.id,
                "is_closed": batch.is_closed,
                "closed_at": batch.closed_at.isoformat() if batch.closed_at else "",
                "task_description": batch.task_description,
                "work_center_id": batch.work_center_id,
                "shift": batch.shift,
                "team": batch.team,
                "batch_number": batch.batch_number,
                "batch_date": batch.batch_date.isoformat(),
                "nomenclature": batch.nomenclature,
                "ekn_code": batch.ekn_code,
                "shift_start": batch.shift_start.isoformat(),
                "shift_end": batch.shift_end.isoformat(),
                "created_at": batch.created_at.isoformat(),
                "updated_at": batch.updated_at.isoformat(),
            })
