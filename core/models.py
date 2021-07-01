from django.db import models
from django.contrib.auth.models import User


class DomainEntity(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Server(DomainEntity):
    owner = models.ForeignKey(User, related_name='server_owner', on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    address = models.URLField()

    def __str__(self):
        return self.name


class Task(DomainEntity):
    task_name = models.CharField(max_length=50)
    server = models.ManyToManyField(Server, related_name='server_task')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.task_name


class Schedule(DomainEntity):
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
