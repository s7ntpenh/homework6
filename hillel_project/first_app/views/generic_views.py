from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, FormView

from first_app.models import Employee
from first_app.forms import EmployeeForm
from first_app.utils import is_user_superuser
from first_app.mixins import UserIsAdminMixin
from first_app.forms import SalaryForm
from first_app.salary_calculator import CalculateMonthRateSalary


class EmployeeListView(ListView):
    model = Employee
    template_name = "employee_list.html"
    context_object_name = "employees"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(position__title__icontains=search),
            )
        return queryset


class EmployeeCreateView(UserIsAdminMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')



class EmployeeUpdateView(UserIsAdminMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')


class EmployeeDeleteView(UserIsAdminMixin, DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')



class SalaryCalculatorView(UserIsAdminMixin, FormView):
    template_name = "salary_calculator.html"
    form_class = SalaryForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})


    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        employee = cleaned_data.get("employee")


        calc = CalculateMonthRateSalary(employee=employee)
        days = {day: day_type for day, day_type in cleaned_data.items() if day.startswith("day_")}

        salary = calc.calculate_salary(days_dict=days)
        return render(
            request=self.request,
            template_name=self.template_name,
            context={'form': form, 'calculated_salary': salary}
        )


