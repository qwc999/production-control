import csv
from datetime import datetime, timezone, date
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.work_center_repository import WorkCenterRepository


REQUIRED_COLUMNS = {
    "is_closed",
    "task_description",
    "work_center_identifier",
    "work_center_name",
    "shift",
    "team",
    "batch_number",
    "batch_date",
    "nomenclature",
    "ekn_code",
    "shift_start",
    "shift_end",
}


class ImportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_repo = BatchRepository(session)
        self.work_center_repo = WorkCenterRepository(session)

    async def import_batches_from_csv(
            self,
            file_path: Path,
            callback=None
    ) -> dict:
        created, skipped = 0, 0
        errors = []

        with file_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if REQUIRED_COLUMNS - set(reader.fieldnames):
                return {
                    "success": False,
                    "total_rows": 0,
                    "created": 0,
                    "skipped": 0,
                    "errors": [
                        {
                            "row": 0,
                            "error": "Wrong headers",
                        }
                    ],
                }

            rows = list(reader)
            total_rows = len(rows)

            for index, row in enumerate(rows, start=1):
                try:
                    work_center = await self.work_center_repo.get_one_or_create(
                        identifier=row["work_center_identifier"],
                        name=row["work_center_name"],
                    )

                    is_closed = row["is_closed"].lower() == "true"

                    batch_data = {
                        "is_closed": is_closed,
                        "closed_at": datetime.now(timezone.utc) if is_closed else None,
                        "task_description": row["task_description"],
                        "work_center_id": work_center.id,
                        "shift": row["shift"],
                        "team": row["team"],
                        "batch_number": int(row["batch_number"]),
                        "batch_date": date.fromisoformat(row["batch_date"]),
                        "nomenclature": row["nomenclature"],
                        "ekn_code": row["ekn_code"],
                        "shift_start": datetime.fromisoformat(row["shift_start"].replace("Z", "+00:00")),
                        "shift_end": datetime.fromisoformat(row["shift_end"].replace("Z", "+00:00"))
                    }

                    await self.batch_repo.create(batch_data)
                    created += 1

                except IntegrityError:
                    await self.session.rollback()
                    skipped += 1
                    errors.append({
                        "row": index,
                        "error": "Duplicate batch number and date",
                    })

                if callback is not None:
                    callback(
                        index,
                        total_rows,
                        created,
                        skipped
                    )

        return {
            "success": True,
            "total_rows": total_rows,
            "created": created,
            "skipped": skipped,
            "errors": errors
        }