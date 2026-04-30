from datetime import datetime

from pydantic import BaseModel, field_serializer

from app.core.time_format import format_datetime


class TimestampOutMixin(BaseModel):
    @field_serializer("created_at", "updated_at", check_fields=False)
    def serialize_timestamp(self, value: datetime | None) -> str | None:
        return format_datetime(value)
