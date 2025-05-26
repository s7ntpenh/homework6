from django.urls import path, include
from rest_framework.routers import DefaultRouter

from first_app.api_views.employee import EmployeeViewSet
from first_app.api_views.position import PositionViewSet

from first_app.api_views.salary import SalaryCalculatorView

router = DefaultRouter()
router.register('employees', EmployeeViewSet)
router.register('positions', PositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('calc-salary/', SalaryCalculatorView.as_view())
]