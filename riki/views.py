from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
import time

from .models import *
from django.forms.formsets import formset_factory
from django.forms import modelformset_factory
from django import forms
from django.http.response import HttpResponse


@login_required
def home(request):
    
    my_courses = Course.objects.filter(
        application__in=request.user.usersemester_set.all().values('application')).order_by('-year','-semester')
    
    my_projects = [c.work for c in request.user.collaboration_set.all().reverse()]
        
    workform = WorkForm(courserestrict=my_courses,actuser=request.user)

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        wf = WorkForm(request.POST)
        if wf.is_valid():
            work = wf.save()
            return redirect('riki:project',project_id=work.id)
        
    
    return render(request, 'riki/home.html',{'user':request.user,
                                             'my_courses':my_courses,
                                             'my_projects':my_projects,
                                             'course_dict':{'kind':'course'},
                                             'project_dict':{'kind':'project'},
                                             'workform':workform,
                                             })

@login_required
def courses(request):
    courses = Course.objects.get_queryset()
    course_typedict = {'kind':'course',
                       'filters':{'.semester-1':'1st Semester',
                                 '.semester-2':'2nd Semester'},
                       'sorters':{'maxallowed':['data-max-allowed','Maximum'],
                                 'semester':['data-semester','Semester'],
                                 'name':['data-cname','Name'],
                                 'year':['data-year','Year']
                           }}
    
    
    return render(request, 'riki/courses.html',
                            {'user':request.user,
                            'courses':courses,
                            'course_typedict':course_typedict})

@login_required
def projects(request):
    works = Work.objects.get_queryset()
    project_typedict = {'kind':'project',
                       'filters':{'.hascourse':'Course Related',
                                 ':not(.hascourse)':'Not Course Related'},
                       'sorters':{'latest':['data-latest','Latest']
                           }}
    return render(request, 'riki/projects.html',
                            {'user':request.user,
                             'projects':works,
                             'project_typedict':project_typedict})

@login_required
def profiles(request):
    return home(request)
    return render(request, 'riki/profiles.html',{'user':request.user})


@login_required
def course(request,course_id):
    return courses(request)
    return render(request, 'riki/course.html',{'user':request.user,
                                               'course_id':course_id})


@login_required
def profile(request,user_id):
    return profiles(request)
    return render(request, 'riki/profile.html',{'user':request.user,
                                                'user_id':user_id})

@login_required
def attribute(request,att_id):
    return home(request)
    return render(request, 'riki/attribute.html',{'user':request.user,
                                                'att_id':att_id})

@login_required
def version(request,version_id):
    v = get_object_or_404(Version,id=version_id)
    fp = open(v.link, 'rb')
    #with open(v.link, 'rb') as fp:
    #    r_file = fp.read()
    filename = '%s - %s.%s' % (v.work.title,v.title,v.link.split('.')[-1])
    filename = '%d.%s' % (v.id,v.link.split('.')[-1])
    response = HttpResponse(fp)
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    print(response['Content-Disposition'])
    print(filename) # force browser to download file
    #response.write(r_file)
    return response

@login_required
def project(request,project_id):
    work = get_object_or_404(Work, id=project_id)
    
    edit = False
    
    if 'edit' in request.GET and request.user in work.collaborators.all():
        edit = True
    

    if request.method == 'POST':
        if 'abstract' in request.POST:
            if request.POST['but'] == 'delete':
                work.delete()
                return redirect('riki:home')
            else:
                form = WorkForm(request.POST or None, instance=work)
                if form.is_valid():
                    form.save()
        else:
            if 'file_upload' in request.FILES:
                file_ext = str(request.FILES['file_upload']).split('.')[-1]
            
            
            if request.POST['but'] == 'create':
                form = VersionForm(request.POST, request.FILES)
                print(form.is_valid())
                if form.is_valid() and 'file_upload' in request.FILES:
                    nv = form.save(commit=False)
                    nv.work = work
                    nv.update_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    nv.save()
                    filelink = 'uploads/%d.%s' % (nv.id,file_ext)
                    nv.link = filelink
                    nv.save()
                    handle_uploaded_file(request.FILES['file_upload'],filelink)

            
            elif request.POST['but'] == 'delete':
                nv = get_object_or_404(Version, id=request.POST['version_id'])
                if request.user in nv.work.collaborators.all():
                    nv.delete()
            
            elif request.POST['but'] == 'modify':
                nv = get_object_or_404(Version, id=request.POST['version_id'])
                form = VersionForm(request.POST or None, instance=nv)
                modified = form.save(commit=False)
                modified.update_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                if form.is_valid():
                    if 'file_upload' in request.FILES:
                        filelink = 'uploads/%d.%s' % (modified.id,file_ext)
                        modified.link = filelink
                        handle_uploaded_file(request.FILES['file_upload'],filelink)
                    modified.save()
    
    workform = WorkForm(instance=work)
    versionforms = [VersionForm] + [VersionForm(instance=v) for v in
                                    work.version_set.all()]
    
    return render(request, 'riki/project.html',{'user':request.user,
                                                'form':workform,
                                                'formset':versionforms,
                                                'edit':edit,
                                                'project':work})




class WorkForm(ModelForm):
    
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

class VersionForm(ModelForm):
    
    file_upload = forms.FileField(required=False)
    
    class Meta:
        model = Version
        fields = ['title', 'comment', 'type','id']
        widgets = {
            'title':forms.Textarea(attrs={'cols':80,'rows':2}),
            'comment':forms.Textarea(attrs={'cols':50,'rows':1}),
            'update_time':forms.HiddenInput()
            }


def handle_uploaded_file(f,link):
    with open(link, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)