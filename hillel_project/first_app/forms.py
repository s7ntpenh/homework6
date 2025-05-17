from datetime import date
import calendar
from django import forms
from django.forms import ChoiceField

from first_app.models import Employee

from common.enums import WorkDayEnum


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('username', 'first_name', 'last_name', 'email', 'position')


class SalaryForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="Employee",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()
        _, num_days = calendar.monthrange(today.year, today.month)
        for day in range(1, num_days + 1):
            day_coord = (today.year, today.month, day)
            weekday = calendar.weekday(*day_coord)
            weekday_name = calendar.day_name[weekday]
            field_name = f"day_{day}"

            if weekday >= 5:
                self.fields[field_name] = ChoiceField(
                    label=f'{day} - {weekday_name}',
                    choices=[(WorkDayEnum.WEEKEND.name, WorkDayEnum.WEEKEND.value)],
                    initial=WorkDayEnum.WEEKEND.name,
                )
            else:
                self.fields[field_name] = ChoiceField(
                    label=f'{day} - {weekday_name}',
                    choices=[(opt.name, opt.value) for opt in WorkDayEnum],
                    initial=WorkDayEnum.WORKING_DAY.name,
                )

    def clean_employee(self):
        employee = self.cleaned_data.get('employee')
        if not employee:
            raise forms.ValidationError("Будь ласка, оберіть працівника.")
        return employee

    def clean(self):
        cleaned_data = super().clean()
        sick_days = 0
        holidays = 0

        for name, value in cleaned_data.items():
            if name.startswith('day_') and value:
                if value == WorkDayEnum.SICK_DAY.name:
                    sick_days += 1
                elif value == WorkDayEnum.HOLIDAY.name:
                    holidays += 1

        if sick_days > 5:
            raise forms.ValidationError(
                f"Кількість лікарняних днів ({sick_days}) перевищує дозволений максимум (5)."
            )

        if holidays > 3:
            raise forms.ValidationError(
                f"Кількість днів відпочинку ({holidays}) перевищує дозволений максимум (3)."
            )

        return cleaned_data