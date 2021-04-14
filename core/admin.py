from __future__ import unicode_literals
from .models import Server, Task
from django.contrib import admin

admin.site.register(Server)
admin.site.register(Task)
