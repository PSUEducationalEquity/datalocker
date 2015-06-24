from django.contrib import admin
from .models import Locker, Submission

# Register your models here.
admin.site.register(Locker)
admin.site.register(Submission)