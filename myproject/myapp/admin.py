from django.urls import path
from django.shortcuts import render
from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .forms import UserCreationForm




admin.site.register(Ticket)

admin.site.register(Agent)
admin.site.register(Technician)
admin.site.register(Supervisor)
admin.site.register(CustomUser)
