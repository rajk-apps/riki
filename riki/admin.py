from django.contrib import admin
from .models import *

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    pass

@admin.register(SemesterConfig)
class SemesterConfigAdmin(admin.ModelAdmin):
    pass