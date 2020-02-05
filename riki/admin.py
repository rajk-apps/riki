from django.contrib import admin
from .models import *


def preapps_to_att(modeladmin, request, queryset):
    for semconf in queryset:
        preapps = Preapplication.objects.filter(user_semester__in=UserSemester.objects.filter(year=semconf.year, semester=semconf.semester))
        for app in preapps:
            if not CourseAttendance.objects.filter(user_semester=app.user_semester, course=app.course):
                start_year = app.user_semester.user.path_set.filter(institution__in=app.course.institution.all()).order_by("yearfrom").first().yearfrom
                ca = CourseAttendance(
                    user_semester=app.user_semester,
                    course=app.course,
                    app_type="1-pref",
                    app_comment='{} - [{}]'.format(app.preference, start_year)
                )
                ca.save()


preapps_to_att.short_description = "Move preapplications to attendances"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    pass


@admin.register(SemesterConfig)
class SemesterConfigAdmin(admin.ModelAdmin):
    actions = [preapps_to_att]


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
