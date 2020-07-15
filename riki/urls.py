from django.urls import path

from . import views

app_name = "riki"
urlpatterns = [
    path("", views.home, name="home"),
    path("courses", views.courses, name="courses"),
    path("profiles", views.profiles, name="profiles"),
    path("projects", views.projects, name="projects"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("course/<int:course_id>", views.course, name="course"),
    path("att/<int:att_id>", views.attribute, name="att_page"),
    path("project/<int:project_id>", views.project, name="project"),
    path("uploads/<int:version_id>", views.version, name="version"),
    path("application_data", views.application_data, name="application_data"),
    path("course_attendance_data", views.ca_data, name="ca_data"),
]
