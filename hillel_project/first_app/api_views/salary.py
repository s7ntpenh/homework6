from rest_framework.response import Response
from rest_framework.views import APIView

from first_app.serializers import SalarySerializer

from first_app.salary_calculator import CalculateMonthRateSalary

from first_app.pydantic_models import WorkingDays


class SalaryCalculatorView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SalarySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        calculator = CalculateMonthRateSalary(employee=serializer.validated_data['employee'])
        month_days = WorkingDays(
            working=serializer.validated_data["working_days"],
            sick=serializer.validated_data["sick_days"],
            holiday=serializer.validated_data["holidays_days"],
            vacation=serializer.validated_data["vacation_days"],
        )
        salary = calculator.calculate_salary(month_days=month_days)
        return Response({"salary": salary})