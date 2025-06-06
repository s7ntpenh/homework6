from django.db import models
from django.core.exceptions import ValidationError

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    tax_code = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and Company.objects.exists():
            raise ValidationError('There can be only one Company instance.')
        return super(Company, self).save(*args, **kwargs)

    def __str__(self):
        return self.name