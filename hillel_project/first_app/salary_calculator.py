import datetime
import logging
from abc import (
    ABC,
    abstractmethod,
)
from math import ceil

from common.enums import WorkDayEnum
from first_app.models import (
    Employee,
    MonthlySalary,
)
from first_app.pydantic_models import WorkingDays


logger = logging.getLogger(__name__)


class AbstractSalaryCalculate(ABC):
    sick_days_multiplier = 0.6
    vacation_days_multiplier = 0.8
    day_prefix = 'day_'

    def __init__(self, employee: Employee):
        self.employee = employee

    @abstractmethod
    def calculate_salary(self, days_dict: dict[str, int]):
        raise NotImplementedError()


class CalculateMonthRateSalary(AbstractSalaryCalculate):
    def __init__(self, employee: Employee):
        super().__init__(employee=employee)
        self._daily_salary = 0

    @staticmethod
    def _calculate_base_work_days(days_dict: dict[str, int]):
        return len(
            {
                day: work_type
                for day, work_type in days_dict.items()
                if work_type not in (WorkDayEnum.HOLIDAY.name, WorkDayEnum.WEEKEND.name)
            },
        )

    def _calculate_daily_salary(self, base_working_days: int) -> int:
        return ceil(self.employee.position.monthly_rate / base_working_days)

    @staticmethod
    def _calculate_monthly_working_days(days_dict: dict[str, int]) -> int:
        return len(
            {day: work_type for day, work_type in days_dict.items() if work_type == WorkDayEnum.WORKING_DAY.name},
        )

    @staticmethod
    def _calculate_monthly_sick_days(days_dict: dict[str, int]) -> int:
        return len(
            {day: work_type for day, work_type in days_dict.items() if work_type == WorkDayEnum.SICK_DAY.name},
        )

    @staticmethod
    def _calculate_monthly_vacation_days(days_dict: dict[str, int]) -> int:
        return len(
            {day: work_type for day, work_type in days_dict.items() if work_type == WorkDayEnum.VACATION.name},
        )

    def _calculate_sick_daily_salary(self) -> int:
        return ceil(self._daily_salary * self.sick_days_multiplier)

    def _calculate_vacation_daily_salary(self) -> int:
        return ceil(self._daily_salary * self.vacation_days_multiplier)

    def _calculate_sick_monthly_salary(self, sick_days: int) -> int:
        return self._calculate_sick_daily_salary() * sick_days

    def _calculate_vacation_monthly_salary(self, vacation_days: int) -> int:
        return self._calculate_vacation_daily_salary() * vacation_days

    def _calculate_working_monthly_salary(self, working_days: int) -> int:
        return working_days * self._daily_salary

    def get_days_count(self, days_dict) -> WorkingDays:
        working_days = self._calculate_monthly_working_days(days_dict=days_dict)
        sick_days = self._calculate_monthly_sick_days(days_dict=days_dict)
        vacation_days = self._calculate_monthly_vacation_days(days_dict=days_dict)

        return WorkingDays(
            working=working_days,
            sick=sick_days,
            vacation=vacation_days,
        )

    def calculate_salary(self, month_days: WorkingDays) -> int:
        self._daily_salary = self._calculate_daily_salary(base_working_days=month_days.base_working_days)

        working_days_salary = self._calculate_working_monthly_salary(working_days=month_days.working)
        sick_monthly_salary = self._calculate_sick_monthly_salary(sick_days=month_days.sick)
        holiday_monthly_salary = self._calculate_vacation_monthly_salary(vacation_days=month_days.vacation)

        salary = sum(
            (
                working_days_salary,
                sick_monthly_salary,
                holiday_monthly_salary,
            ),
        )

        return salary if salary <= self.employee.position.monthly_rate else self.employee.position.monthly_rate

    def save_salary(self, salary: int, date: datetime.date):
        month_date = date.replace(day=1)
        try:
            MonthlySalary.objects.get(month_year=month_date, employee=self.employee, paid=True)
        except MonthlySalary.DoesNotExist:
            MonthlySalary.objects.update_or_create(
                month_year=month_date,
                employee=self.employee,
                defaults={'salary': salary, 'paid': False},
            )
            logger.info(
                msg=f'Salary for employee {self.employee} for {month_date.month}/{month_date.year} created.',
            )
        else:
            logger.warning(
                msg=f'Salary for employee {self.employee} for {month_date.month}/{month_date.year} already paid.',
            )
