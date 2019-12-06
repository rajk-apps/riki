from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
import time

from .models import *
from .forms import *
from django.http.response import HttpResponse

@login_required
def home(request):
    
    my_courses = Course.objects.filter(
        application__in=request.user.usersemester_set.all().values('application')).order_by('-year','-semester')
    
    my_projects = [c.work for c in request.user.collaboration_set.all().reverse()]
        
    workform = WorkForm(courserestrict=my_courses, actuser=request.user)

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        wf = WorkForm(request.POST)
        if wf.is_valid():
            work = wf.save(commit=False)
            work.save()
            for collaborator in wf.cleaned_data.get('collaborators'):
                collab_link = Collaboration(work=work, user=collaborator)
                collab_link.save()
            return redirect('riki:project',project_id=work.id)
        
    
    return render(request, 'riki/home.html',{'user':request.user,
                                             'my_courses':my_courses,
                                             'my_projects':my_projects,
                                             'course_dict':{'griditem_template':'riki/course-griditem.html'},
                                             'project_dict':{'griditem_template':'riki/project-griditem.html'},
                                             'workform':workform,
                                             })

@login_required
def courses(request):
    
    if request.method == 'POST':
        tosub = request.POST['apply_button']
        act_course = Course.objects.get(pk=tosub)
        act_semester = UserSemester.objects.get(user=request.user.id,
                                                year=act_course.year,
                                                semester=act_course.semester)
        applicants = [_c.user_semester.user.id for _c in 
                      act_course.courseattendance_set.all()]
        if request.user.id in applicants:
            if len(applicants) <= act_course.minapplicants:
                #WARNING BERAGADÁS
                pass
            else:
                Application(user_semester=act_semester,course=act_course,
                            app_type='drop',
                            time=time.strftime('%Y-%m-%d %H:%M:%S')).save()
                CourseAttendance.objects.get(user_semester=act_semester,
                                 course=act_course).delete()
        else:
            Application(user_semester=act_semester,course=act_course,
                        app_type='apply',
                        time=time.strftime('%Y-%m-%d %H:%M:%S')).save()
            CourseAttendance(user_semester=act_semester,course=act_course,
                             app_type='2-corr',
                             app_comment=time.strftime('%Y-%m-%d %H:%M:%S')).save()
    
    poss = set(SemesterConfig.objects.all().values_list('year','institution'))
    for_select = {}
    for k,ind in {'year':0,'inst':1}.items():
        for_select[k] = [p[ind] for p in poss]
        for_select[k].sort()

    if request.method == 'GET' \
                    and 'year' in request.GET and 'inst' in request.GET:
        act_inst = request.GET['inst']
        act_year = request.GET['year']
    else:
        act_inst = for_select['inst'][0]
        act_year = for_select['year'][-1]
    courses = Course.objects.filter(year=act_year,institution=act_inst)
    
    #TODO: very slow, quite shit, make it better!
    sconfs = SemesterConfig.objects.filter(year=act_year,institution=act_inst)
    open_semesters = [sc.semester for sc in sconfs if sc.app_open]
    for c in courses:
        if c.is_attending(request.user):
            c.am_attending = True
        if c.semester in open_semesters:
            c.is_open = True
        
    for_select['year'] = [(y,'%d/%d' % (y,y+1)) for y in set(for_select['year'])]
    for_select['inst'] = [(idx,Institution.objects.get(pk=idx).shortname)
                           for idx in set(for_select['inst'])]
    
    course_filter_form = CourseFilter(for_select,initial={'year':act_year,
                                                         'inst':act_inst})
    
    course_typedict = {'filters':{'.semester-1':'1st Semester',
                                 '.semester-2':'2nd Semester',
                                 '.attending-1':'I Applied',
                                 '.space-1':'Not full',
                                 '.nogo-1':'Too few'},
                       'sorters':{'semester':['data-semester','Semester'],
                                 'name':['data-cname','Name'],
                                 'currentapplicants':['data-currentapplicants','Applicants']},
                        'griditem_template':'riki/course-griditem.html'}
    
    
    return render(request, 'riki/gridpage.html',
                            {'user':request.user,
                            'queryset':courses,
                            'typedict':course_typedict,
                            'filterform':course_filter_form,
                            'navtitle':'Courses'})

@login_required
def projects(request):
    works = Work.objects.get_queryset()
    project_typedict = {'griditem_template':'riki/project-griditem.html',
                       'filters':{'.hascourse':'Course Related',
                                 ':not(.hascourse)':'Not Course Related'},
                       'sorters':{'latest':['data-latest','Latest']
                           }}
    return render(request, 'riki/gridpage.html',
                            {'user':request.user,
                             'queryset':works,
                             'typedict':project_typedict,
                             'navtitle':'Projects'})

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


def handle_uploaded_file(f,link):
    with open(link, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)