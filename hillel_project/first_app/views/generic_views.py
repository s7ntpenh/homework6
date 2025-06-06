import logging
import datetime

from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, FormView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.shortcuts import redirect

from first_app.models import Employee, Company
from first_app.forms import EmployeeForm
from first_app.mixins import UserIsAdminMixin
from first_app.forms import SalaryForm

from first_app.salary_calculator import CalculateMonthRateSalary

logger = logging.getLogger('default')

@method_decorator(cache_page(180), name="dispatch")
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
        logger.info(f"Render employees list for user {self.request.user}")
        return queryset


class EmployeeCreateView(UserIsAdminMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')

    def form_valid(self, form):
        messages.success(self.request, "Працівник створено успішно!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Виникла помилка при створенні, спробуйте ще раз!")
        return super().form_invalid(form)

class EmployeeUpdateView(UserIsAdminMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employee_list')

    def form_valid(self, form):
        messages.success(self.request, "Iнформація про працівника оновлена успішно!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Виникла помилка при оновленні інформації, спробуйте ще раз!")
        return super().form_invalid(form)

class EmployeeDeleteView(UserIsAdminMixin, DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')


class EmployeeDetailsView(UserIsAdminMixin, DetailView):
    model = Employee
    template_name = "employee_details.html"


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
        calc.save_salary(salary, datetime.date.today())
        return render(
            request=self.request,
            template_name=self.template_name,
            context={'form': form, 'calculated_salary': salary}
        )

class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.first()
        context['company'] = company
        return context
