import time
import re

from ..models import (
    Course,
    UserSemester,
    Application,
    CourseAttendance,
    Preapplication,
    Path
)
from ..forms import PreappForm


def handle_course_applictaion(request):
    course_id = request.POST["course_id"]
    tosub = request.POST["apply_button"]
    act_course = Course.objects.get(pk=course_id)
    act_semester = UserSemester.objects.get(
        user=request.user.id,
        year=act_course.year,
        semester=act_course.semester,
    )
    applicants = [
        _c.user_semester.user.id
        for _c in act_course.courseattendance_set.all()
    ]
    if (request.user.id in applicants) and (tosub == "drop"):
        if len(applicants) <= act_course.minapplicants:
            # WARNING BERAGADÁS
            pass
        else:
            Application(
                user_semester=act_semester,
                course=act_course,
                app_type="drop",
                time=time.strftime("%Y-%m-%d %H:%M:%S"),
            ).save()
            CourseAttendance.objects.get(
                user_semester=act_semester, course=act_course
            ).delete()
    elif (request.user.id not in applicants) and (tosub == "apply"):
        Application(
            user_semester=act_semester,
            course=act_course,
            app_type="apply",
            time=time.strftime("%Y-%m-%d %H:%M:%S"),
        ).save()
        CourseAttendance(
            user_semester=act_semester,
            course=act_course,
            app_type="2-corr",
            app_comment=time.strftime("%Y-%m-%d %H:%M:%S"),
        ).save()


def handle_course_preapp(request):
    form_id_rex = re.compile(r"(\d)-(.*)-.*-course")
    uset = []
    preapps = []
    for k, course in request.POST.items():
        res = form_id_rex.findall(k)
        if res:
            us_id = res[0][1]
            uset.append(us_id)
            if course:
                pref_no = int(res[0][0])
                act_semester = UserSemester.objects.get(pk=us_id)
                preapp = Preapplication(
                    user_semester=act_semester, course_id=course, preference=pref_no
                )
                preapps.append(preapp)
    Preapplication.objects.filter(user_semester__in=uset).delete()
    CourseAttendance.objects.filter(
        user_semester__in=uset,
    ).delete()
    for preapp in preapps:
        preapp.save()
        act_course = Course.objects.get(pk=preapp.course_id)
        user_path = Path.objects.filter(user=request.user.id, institution__in=act_course.institution.all())
        if len(user_path):
            secondary_num = user_path[0].yearfrom
            app_comment = f"{preapp.preference} - {secondary_num}"
        else:
            app_comment = f"XENO - {preapp.preference}"
        CourseAttendance(
            user_semester=preapp.user_semester,
            course=act_course,
            app_type="1-pref",
            app_comment=app_comment,
        ).save()


def get_preapp_formlists(preapp_open_semester_configs, user):
    preapp_formlists = []
    for sc in preapp_open_semester_configs:
        act_semester = UserSemester.objects.get(
            user=user.id, year=sc.year, semester=sc.semester,
        )
        user_preapps = Preapplication.objects.filter(
            user_semester=act_semester
        )
        open_course_set = Course.objects.filter(
            semester=sc.semester, year=sc.year, institution=sc.institution
        )
        semester_list = []
        for title, pref_no in [
            ("1st preference", 1),
            ("2nd preference", 2),
            ("3rd preference", 3),
            ("4th preference", 4),
            ("5th preference", 5),
            ("extra 1st preference", 1),
        ]:
            relevant_preapp = user_preapps.filter(preference=pref_no)
            if title == "extra 1st preference":
                pr_ind = 1
            else:
                pr_ind = 0
            try:
                init_course = relevant_preapp[pr_ind].course
            except IndexError:
                init_course = None

            new_form = PreappForm(
                courserestrict=open_course_set,
                initial_course=init_course,
                prefix=f"{pref_no}-{act_semester.id}-{title[:1]}",
            )
            new_form.pref_name = title
            semester_list.append(new_form)

        preapp_formlists.append(PreappFormlist(semester_list, sc))

    return preapp_formlists


class PreappFormlist:
    def __init__(self, formlist, sconf):
        self._formlist = formlist
        self._sconf = sconf

    def __iter__(self):
        for f in self._formlist:
            yield f

    @property
    def name(self):
        return f"{self._sconf.year}/{self._sconf.year + 1} - {self._sconf.semester}"
