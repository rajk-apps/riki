from django.contrib.auth.models import User
from django.db import models


class Institution(models.Model):

    longname = models.CharField(max_length=100)
    shortname = models.CharField(max_length=20)
    website = models.CharField(max_length=100)
    members = models.ManyToManyField(User, through="Path")

    def __str__(self):
        return self.shortname


class Path(models.Model):

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    yearfrom = models.PositiveIntegerField()
    yearto = models.PositiveIntegerField(null=True, blank=True)

    graduated = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s - %s (%d)" % (
            self.user.first_name,
            self.user.last_name,
            self.institution.shortname,
            self.yearfrom,
        )


###
# COURSE APPLICATIONS
###


class Course(models.Model):

    am_attending = False
    is_open = False

    teachers = models.ManyToManyField(User, related_name="teacher")
    institution = models.ManyToManyField("Institution")

    year = models.PositiveIntegerField()
    semester = models.PositiveSmallIntegerField()
    minapplicants = models.PositiveSmallIntegerField()
    maxapplicants = models.PositiveSmallIntegerField()
    juniority = models.BooleanField(default=False)

    syllabus = models.CharField(max_length=250)
    name = models.CharField(max_length=100)
    comment = models.CharField(max_length=250, null=True, blank=True)
    language = models.CharField(max_length=3, default="HU")

    attribute = models.ManyToManyField("AttributeTag", blank=True)

    def __str__(self):
        return "%s (%d, %d) - %s" % (
            self.name,
            self.year,
            self.semester,
            ",".join([i.shortname for i in self.institution.all()]),
        )

    def current_members(self):

        # if self.juniority:
        #    ...  # TODO!!!!

        return [
            {
                "user": u.user_semester.user,
                "plus_info": f"{u.get_app_type_display()} - {u.app_comment}",
                "result": u.result,
            }
            for u in self.courseattendance_set.order_by(
                "app_type", "app_comment"
            )
        ]

    def is_attending(self, user):
        return user in [
            u.user_semester.user for u in self.courseattendance_set.all()
        ]

    def get_filtertags(self):
        currnum = len(self.current_members())

        return [
            "semester-%d" % self.semester,
            "attending-%d" % int(self.am_attending),
            "space-%d" % int(currnum < self.maxapplicants),
            "nogo-%d" % int(currnum < self.minapplicants),
        ]

    def get_sortdict(self):
        return {
            "data-year": self.year,
            "data-cname": self.name,
            "data-semester": self.semester,
            "data-currentapplicants": "{:03}".format(
                len(self.current_members())
            ),
        }


class UserSemester(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    semester = models.PositiveSmallIntegerField()

    preapplications = models.ManyToManyField(
        Course,
        related_name="semester_preapplication",
        through="Preapplication",
    )
    applications = models.ManyToManyField(
        Course, related_name="semester_application", through="Application"
    )
    attendance = models.ManyToManyField(
        Course, related_name="semester_attendance", through="CourseAttendance"
    )

    def __str__(self):
        return (
            self.user.email
            + " - "
            + str(self.year)
            + " - "
            + str(self.semester)
        )


class Preapplication(models.Model):

    user_semester = models.ForeignKey(UserSemester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    preference = models.PositiveSmallIntegerField()

    def __str__(self):
        return " - ".join(
            [str(self.user_semester), self.course.name, str(self.preference)]
        )


class Application(models.Model):

    user_semester = models.ForeignKey(UserSemester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    time = models.DateTimeField()

    APP_CHOICE = [("apply", "apply"), ("drop", "drop")]

    app_type = models.CharField(
        max_length=10, choices=APP_CHOICE, default="apply"
    )

    def __str__(self):
        return " - ".join(
            [
                str(self.user_semester),
                self.course.name,
                str(self.time),
                self.app_type,
            ]
        )


class CourseAttendance(models.Model):

    user_semester = models.ForeignKey(UserSemester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    RESULT_CHOICE = [
        ("TBD", "TBD"),
        ("pass", "pass"),
        ("fail", "fail"),
        ("distinction", "distinction"),
    ]

    result = models.CharField(
        max_length=20, choices=RESULT_CHOICE, default="TBD"
    )

    APP_CHOICE = [("1-pref", "Preference-based"), ("2-corr", "Time-based")]

    app_type = models.CharField(
        max_length=20, choices=APP_CHOICE, default="2-corr"
    )

    app_comment = models.CharField(
        max_length=40, default="", blank=True, null=True
    )

    def __str__(self):
        return (
            str(self.user_semester)
            + " - "
            + self.course.name
            + " - "
            + str(self.result)
        )

    def works(self):
        return "the works from this"


class SemesterConfig(models.Model):

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    semester = models.PositiveSmallIntegerField()

    preapp_open = models.BooleanField(default=False)
    app_open = models.BooleanField(default=False)

    specially_open = models.ManyToManyField("Course", blank=True)

    specially_open_for_person = models.ManyToManyField(User, blank=True)

    specially_closed_for_person = models.ManyToManyField(
        User, blank=True, related_name="outcast"
    )

    def __str__(self):
        return "%s - %d - %d" % (
            self.institution.shortname,
            self.year,
            self.semester,
        )


###
# PROJECTS:
###


class Work(models.Model):

    title = models.CharField(max_length=200)
    abstract = models.TextField()

    courses = models.ManyToManyField(Course)
    collaborators = models.ManyToManyField(User, through="Collaboration")
    attribute = models.ManyToManyField("AttributeTag")

    def __str__(self):
        return self.title

    def get_filtertags(self):
        out = []
        if len(self.courses.all()) > 0:
            out.append("hascourse")
        return out

    def get_sortdict(self):
        try:
            return {"data-latest": self.version_set.last().update_time}
        except:
            return {"data-latest": 0}


class Version(models.Model):

    update_time = models.DateTimeField()
    title = models.CharField(max_length=200)
    comment = models.CharField(max_length=200, null=True, blank=True)
    link = models.CharField(max_length=200)

    V_TYPES = [
        ("paper", "Paper"),
        ("essay", "Essay"),
        ("review", "Review"),
        ("presentation", "Presentation"),
        ("data", "Data"),
        ("publication", "Publication"),
        ("code", "Code"),
        ("competition", "Competition"),
        ("confpaper", "Conference Paper"),
    ]

    type = models.CharField(max_length=40, choices=V_TYPES, default="paper")
    work = models.ForeignKey(Work, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class AttributeTag(models.Model):

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, null=True, blank=True)

    KIND_CHOICES = [("keyword", "keyword"), ("work_merit", "work_merit")]

    kind = models.CharField(
        max_length=20, choices=KIND_CHOICES, default="keyword"
    )

    def __str__(self):
        return self.name


class Collaboration(models.Model):

    COLL_CHOICE = [
        ("author", "Author"),
        ("reviewer", "Reviewer"),
        ("advisor", "Advisor"),
        ("translator", "Translator"),
    ]

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=COLL_CHOICE,
        default="author",
    )
