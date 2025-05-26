import logging
import datetime

from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation.trans_null import gettext_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, FormView, DetailView

from first_app.models import Employee
from first_app.forms import EmployeeForm
from first_app.mixins import UserIsAdminMixin
from first_app.forms import SalaryForm

from first_app.salary_calculator import CalculateMonthRateSalary

logger = logging.getLogger('default')

class EmployeeListView(ListView):
    model = Employee
    template_name = "first_app/employee_list.html"
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
        logger.info(f"Render employees list for user {self.request.user}")
        return queryset


class EmployeeCreateView(UserIsAdminMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'first_app/employee_form.html'
    success_url = reverse_lazy('employee_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.warning(self.request, "Employee creates successfully")
        return response

    def form_invalid(self, form):
        messages.error(self.request, gettext_lazy("employee_create_error"))
        return super().form_invalid(form)





class EmployeeUpdateView(UserIsAdminMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'first_app/employee_form.html'
    success_url = reverse_lazy('employee_list')


class EmployeeDeleteView(UserIsAdminMixin, DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')


class EmployeeDetailsView(UserIsAdminMixin, DetailView):
    model = Employee
    template_name = "first_app/employee_details.html"


    def get_object(self, queryset=None):
        e_id = self.kwargs.get("pk")
        employee = cache.get(f"employee_{e_id}")
        if not employee:
            logger.warning(f"Employee {e_id} NOT IN CACHE")
            employee = get_object_or_404(Employee, pk=e_id)
            cache.set(f"employee_{e_id}", employee, timeout=5)
        else:
            logger.info(f"Employee {e_id} WAS IN CACHE")

        return employee


class SalaryCalculatorView(UserIsAdminMixin, FormView):
    template_name = 'salary_calculator.html'
    form_class = SalaryForm

    def get(self, request, *args, **kwargs):
        form = SalaryForm()
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        employee = cleaned_data.get('employee')

        calculator = CalculateMonthRateSalary(employee=employee)

        days = {day: day_type for day, day_type in cleaned_data.items() if day.startswith(calculator.day_prefix)}

        month_days = calculator.get_days_count(days_dict=days)
        salary = calculator.calculate_salary(month_days=month_days)

        calculator.save_salary(salary=salary, date=datetime.date.today())

        return render(
            request=self.request,
            template_name=self.template_name,
            context={
                'form': form,
                'calculated_salary': salary,
            },
        )