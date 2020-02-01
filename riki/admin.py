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


@admin.register(UserSemester)
class UserSemesterAdmin(admin.ModelAdmin):
    pass


@admin.register(Preapplication)
class PreappAdmin(admin.ModelAdmin):
    pass


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseAttendance)
class CourseAttendanceAdmin(admin.ModelAdmin):
    pass
