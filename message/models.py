from django.db import models
from core.models import DomainEntity


class Consult(DomainEntity):
    name = models.CharField(max_length=16)
    position = models.CharField(max_length=16, null=True)
    group = models.CharField(max_length=50)
    email = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=14)
    describe = models.TextField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)

    def __str__(self): return self.name

    class Meta:
        db_table = 'Consult'

