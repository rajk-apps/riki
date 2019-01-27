from .models import *
from django import forms


class WorkForm(forms.ModelForm):
    
    def __init__(self,*args,actuser=None,courserestrict=Course.objects,**kwargs):
        super(WorkForm,self).__init__(*args,**kwargs)
        self.fields['courses'].queryset = courserestrict
        self.fields['courses'].required = False
        self.fields['attribute'].required = False
        if type(actuser) != type(None):
            self.fields['collaborators'].initial = [actuser]
        
    class Meta:
        model = Work
        exclude = []
        widgets = {
            'title':forms.Textarea(attrs={'cols':80,'rows':2}),
            'abstract':forms.Textarea(attrs={'cols':80,'rows':10}),
            'attribute':forms.SelectMultiple(attrs={
                    'class': 'chosen-select',
                    'multiple tabindex': '4',
                        }),
            'collaborators':forms.SelectMultiple(attrs={
                    'class': 'chosen-select',
                    'multiple tabindex': '4',
                        }),
            'courses':forms.SelectMultiple(attrs={
                    'class': 'chosen-select',
                    'multiple tabindex': '4',
                        })
            }
        #fields = ['title', 'abstract', 'collaborators', 'attributes']

class VersionForm(forms.ModelForm):
    
    file_upload = forms.FileField(required=False)
    
    class Meta:
        model = Version
        fields = ['title', 'comment', 'type','id']
        widgets = {
            'title':forms.Textarea(attrs={'cols':80,'rows':2}),
            'comment':forms.Textarea(attrs={'cols':50,'rows':1}),
            'update_time':forms.HiddenInput()
            }

class CourseFilter(forms.Form):
    
    inst = forms.ChoiceField(label='Institution')
    year = forms.ChoiceField(label='Academic year')
    
    def __init__(self, for_select, **kwargs):
        super(CourseFilter, self).__init__(**kwargs)
        for kw in ['year','inst']:
            self.fields[kw] = forms.ChoiceField(
                choices=for_select[kw],
                
            )