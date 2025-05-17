from enum import StrEnum, auto


class WorkDayEnum(StrEnum):
    WORKING_DAY = auto()
    SICK_DAY = "sick_day"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"
    UNPAID_DAY = "unpaid_day"

