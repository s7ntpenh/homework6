from django.db import models
from django.utils.translation import gettext_lazy as _

class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name department"))
    parent_department = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Parent department"))

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    def __str__(self):
        return self.name
    