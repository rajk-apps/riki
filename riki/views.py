import time
from typing import List

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import WorkForm, VersionForm, CourseFilter
from .core.course_logic import (
    handle_course_applictaion,
    handle_course_preapp,
    get_preapp_formlists,
)
from .models import *


@login_required
def home(request):

    my_courses = (
        Course.objects.filter(
            courseattendance__in=request.user.usersemester_set.all().values(
                "courseattendance"
            )
        )
        .distinct()
        .order_by("-year", "-semester")
    )
    my_projects = [
        c.work for c in request.user.collaboration_set.all().reverse()
    ]

    workform = WorkForm(courserestrict=my_courses, actuser=request.user)

    if request.method == "GET":
        pass
    elif request.method == "POST":
        wf = WorkForm(request.POST)
        if wf.is_valid():
            work = wf.save(commit=False)
            work.save()
            for collaborator in wf.cleaned_data.get("collaborators"):
                collab_link = Collaboration(work=work, user=collaborator)
                collab_link.save()
            return redirect("riki:project", project_id=work.id)

    return render(
        request,
        "riki/home.html",
        {
            "user": request.user,
            "my_courses": my_courses,
            "my_projects": my_projects,
            "course_dict": {"griditem_template": "riki/course-griditem.html"},
            "project_dict": {
                "griditem_template": "riki/project-griditem.html"
            },
            "workform": workform,
        },
    )


@login_required
def courses(request):

    # get semconfs with open preapp
    # make forms
    # process forms based on semconfs (and user)
    # delete all preapps of user
    # add new ones
    # update courseattendance - app comment: PREF_NO, START YEAR

    # somehow make junior courses??

    if request.method == "POST":
        if request.POST["but"] == "Submit Preapplication":
            handle_course_preapp(request)
        else:
            handle_course_applictaion(request)

    all_semester_configs = SemesterConfig.objects.all()
    if len(all_semester_configs) == 0:
        return HttpResponse("No semesterconfig in database")

    if "year" in request.GET and "inst" in request.GET:
        act_inst = request.GET["inst"]
        act_year = request.GET["year"]
    else:
        _act_sconf = all_semester_configs[0]
        act_inst = _act_sconf.institution
        act_year = _act_sconf.year

    course_set = Course.objects.filter(year=act_year, institution=act_inst)
    act_sconfs = SemesterConfig.objects.filter(
        year=act_year, institution=act_inst
    )

    open_semesters = [
        sc.semester
        for sc in act_sconfs
        if (
            (
                sc.app_open
                or (request.user in sc.specially_open_for_person.all())
            )
            and (request.user not in sc.specially_closed_for_person.all())
        )
    ]

    preapp_open_semester_configs = [sc for sc in act_sconfs if sc.preapp_open]

    # TODO: very slow, quite shit, make it better!
    for c in course_set:
        if c.is_attending(request.user):
            c.am_attending = True
        if c.semester in open_semesters:
            if request.user.usersemester_set.filter(
                year=c.year, semester=c.semester
            ):
                c.is_open = True

    course_filter_form = CourseFilter(
        all_semester_configs, initial={"year": act_year, "inst": act_inst}
    )

    course_typedict = {
        "filters": {
            ".semester-1": "1st Semester",
            ".semester-2": "2nd Semester",
            ".attending-1": "I Applied",
            ".space-1": "Not full",
            ".nogo-1": "Too few",
        },
        "sorters": {
            "semester": ["data-semester", "Semester"],
            "name": ["data-cname", "Name"],
            "currentapplicants": ["data-currentapplicants", "Applicants"],
        },
        "griditem_template": "riki/course-griditem.html",
    }

    preapp_formlists = get_preapp_formlists(
        preapp_open_semester_configs, request.user
    )

    return render(
        request,
        "riki/gridpage.html",
        {
            "top_template": "riki/course_preapp_box.html",
            "formlists": preapp_formlists,
            "user": request.user,
            "queryset": course_set,
            "typedict": course_typedict,
            "filterform": course_filter_form,
            "navtitle": "Courses",
        },
    )


@login_required
def projects(request):
    works = Work.objects.get_queryset()
    project_typedict = {
        "griditem_template": "riki/project-griditem.html",
        "filters": {
            ".hascourse": "Course Related",
            ":not(.hascourse)": "Not Course Related",
        },
        "sorters": {"latest": ["data-latest", "Latest"]},
    }
    return render(
        request,
        "riki/gridpage.html",
        {
            "user": request.user,
            "queryset": works,
            "typedict": project_typedict,
            "navtitle": "Projects",
        },
    )


@login_required
def profiles(request):
    return home(request)
    return render(request, "riki/profiles.html", {"user": request.user})


@login_required
def course(request, course_id):
    return courses(request)
    return render(
        request,
        "riki/course.html",
        {"user": request.user, "course_id": course_id},
    )


@login_required
def profile(request, user_id):
    return profiles(request)
    return render(
        request,
        "riki/profile.html",
        {"user": request.user, "user_id": user_id},
    )


@login_required
def attribute(request, att_id):
    return home(request)
    return render(
        request,
        "riki/attribute.html",
        {"user": request.user, "att_id": att_id},
    )


@login_required
def version(request, version_id):
    v = get_object_or_404(Version, id=version_id)
    fp = open(v.link, "rb")
    # with open(v.link, 'rb') as fp:
    #    r_file = fp.read()
    filename = "%s - %s.%s" % (v.work.title, v.title, v.link.split(".")[-1])
    filename = "%d.%s" % (v.id, v.link.split(".")[-1])
    response = HttpResponse(fp)
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename
    print(response["Content-Disposition"])
    print(filename)  # force browser to download file
    # response.write(r_file)
    return response


@login_required
def project(request, project_id):
    work = get_object_or_404(Work, id=project_id)

    edit = False

    if "edit" in request.GET and request.user in work.collaborators.all():
        edit = True

    if request.method == "POST":
        if "abstract" in request.POST:
            if request.POST["but"] == "delete":
                work.delete()
                return redirect("riki:home")
            else:
                form = WorkForm(request.POST or None, instance=work)
                if form.is_valid():
                    form.save()
        else:
            if "file_upload" in request.FILES:
                file_ext = str(request.FILES["file_upload"]).split(".")[-1]

            if request.POST["but"] == "create":
                form = VersionForm(request.POST, request.FILES)
                print(form.is_valid())
                if form.is_valid() and "file_upload" in request.FILES:
                    nv = form.save(commit=False)
                    nv.work = work
                    nv.update_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    nv.save()
                    filelink = "uploads/%d.%s" % (nv.id, file_ext)
                    nv.link = filelink
                    nv.save()
                    handle_uploaded_file(
                        request.FILES["file_upload"], filelink
                    )

            elif request.POST["but"] == "delete":
                nv = get_object_or_404(Version, id=request.POST["version_id"])
                if request.user in nv.work.collaborators.all():
                    nv.delete()

            elif request.POST["but"] == "modify":
                nv = get_object_or_404(Version, id=request.POST["version_id"])
                form = VersionForm(request.POST or None, instance=nv)
                modified = form.save(commit=False)
                modified.update_time = time.strftime("%Y-%m-%d %H:%M:%S")

                if form.is_valid():
                    if "file_upload" in request.FILES:
                        filelink = "uploads/%d.%s" % (modified.id, file_ext)
                        modified.link = filelink
                        handle_uploaded_file(
                            request.FILES["file_upload"], filelink
                        )
                    modified.save()

    workform = WorkForm(instance=work)
    versionforms = [VersionForm] + [
        VersionForm(instance=v) for v in work.version_set.all()
    ]

    return render(
        request,
        "riki/project.html",
        {
            "user": request.user,
            "form": workform,
            "formset": versionforms,
            "edit": edit,
            "project": work,
        },
    )


def handle_uploaded_file(f, link):
    with open(link, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def application_data(request):
    app_list = Application.objects.all()
    app_rec_list = _proc_applist(app_list)
    return JsonResponse(app_rec_list, safe=False)


def _proc_applist(app_list: List[Application]):

    return [
        {
            "user": a.user_semester.user.email,
            "year": a.user_semester.year,
            "semester": a.user_semester.semester,
            "course_name": a.course.name,
            "action": a.app_type,
            "time": a.time,
        }
        for a in app_list
    ]

def ca_data(request):
    ca_list = CourseAttendance.objects.all()
    ca_rec_list = _proc_calist(ca_list)
    return JsonResponse(ca_rec_list, safe=False)


def _proc_calist(app_list: List[CourseAttendance]):

    return [
        {
            "user": a.user_semester.user.email,
            "fname": a.user_semester.user.first_name,
            "lname": a.user_semester.user.last_name,
            "year": a.user_semester.year,
            "semester": a.user_semester.semester,
            "course_name": a.course.name,
            "action": a.app_type,
            "comment": a.app_comment,
        }
        for a in app_list
    ]
