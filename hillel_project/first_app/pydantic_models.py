from pydantic import (
    BaseModel,
    computed_field,
)


class WorkingDays(BaseModel):
    working: int
    sick: int
    vacation: int
    holidays: int = 0

    @computed_field
    @property
    def base_working_days(self) -> int:
        return sum(
            (
                self.working,
                self.sick,
                self.vacation,
            ),
        )
