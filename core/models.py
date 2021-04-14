from django.db import models
from django.contrib.auth.models import User


class DomainEntity(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


class Server(DomainEntity):
    owner = models.ForeignKey(User, related_name='server_owner', on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    address = models.URLField()


class Task(DomainEntity):
    task_name = models.CharField(max_length=50)
    server_name = models.ManyToManyField(Server, related_name='server_task')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.task_name
