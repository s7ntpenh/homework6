from django.db.models import Q
from rest_framework import viewsets

from first_app.models import Employee

from first_app.serializers import EmployeeSerializer, EmployeeLiteSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins


class ExampleViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(position__title__icontains=search),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeLiteSerializer
        else:
            return super().get_serializer_class()

    @action(detail=True, methods=["GET"], url_path="same-position-count")
    def position_count(self, request, pk=None):
        employee = self.get_object()
        count = Employee.objects.filter(position=employee.position).count()
        return Response({"position_count": count})

