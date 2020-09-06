from django import forms

from .models import Course, Preapplication, Version, Work


class WorkForm(forms.ModelForm):
    def __init__(
        self, *args, actuser=None, courserestrict=Course.objects, **kwargs
    ):
        super(WorkForm, self).__init__(*args, **kwargs)
        self.fields["courses"].queryset = courserestrict
        self.fields["courses"].required = False
        self.fields["attribute"].required = False
        if actuser is not None:
            self.fields["collaborators"].initial = [actuser]

    class Meta:
        model = Work
        exclude = []
        widgets = {
            "title": forms.Textarea(attrs={"cols": 80, "rows": 2}),
            "abstract": forms.Textarea(attrs={"cols": 80, "rows": 10}),
            "attribute": forms.SelectMultiple(
                attrs={"class": "chosen-select", "multiple tabindex": "4",}
            ),
            "collaborators": forms.SelectMultiple(
                attrs={"class": "chosen-select", "multiple tabindex": "4",}
            ),
            "courses": forms.SelectMultiple(
                attrs={"class": "chosen-select", "multiple tabindex": "4",}
            ),
        }


class VersionForm(forms.ModelForm):

    file_upload = forms.FileField(required=False)

    class Meta:
        model = Version
        fields = ["title", "comment", "type", "id"]
        widgets = {
            "title": forms.Textarea(attrs={"cols": 80, "rows": 2}),
            "comment": forms.Textarea(attrs={"cols": 50, "rows": 1}),
            "update_time": forms.HiddenInput(),
        }


class CourseFilter(forms.Form):

    inst = forms.ChoiceField(label="Institution")
    year = forms.ChoiceField(label="Academic year")

    def __init__(self, semester_configs, **kwargs):
        super(CourseFilter, self).__init__(**kwargs)
        year_choices = sorted(
            list(
                set(
                    [
                        (sc.year, "%d/%d" % (sc.year, sc.year + 1))
                        for sc in semester_configs
                    ]
                )
            ),
            key=lambda t: t[0],
            reverse=True,
        )
        inst_choices = list(
            set(
                [
                    (sc.institution.pk, sc.institution.shortname)
                    for sc in semester_configs
                ]
            )
        )
        self.fields["year"] = forms.ChoiceField(choices=year_choices)
        self.fields["inst"] = forms.ChoiceField(choices=inst_choices)


class PreappForm(forms.ModelForm):
    def __init__(
        self,
        *args,
        courserestrict=Course.objects,
        initial_course=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = courserestrict
        self.fields["course"].required = False
        if initial_course is not None:
            self.fields["course"].initial = initial_course

    class Meta:
        model = Preapplication
        exclude = []
        fields = ["course"]
        widgets = {
            "preference": forms.HiddenInput(),
        }
