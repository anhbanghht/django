from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import logging
logger = logging.getLogger(__name__)
from django.utils import timezone
import datetime
import re
import collections

from .models import User, Department
from django.db import connection
from .form.from_datepicker import DatePickerForm
from .common.re_common import EMAIL_REGEX

def index(request):
    # listUser = User.objects.order_by('-user_name')[:5]

    condition = {
        'userName': request.GET.get('userName', ''),
        'departmentId': int(request.GET.get('departmentId', '0'))
    }
    departmentChildrent = findDepartmentFromDepartmentParent(condition['departmentId'])
    sql = ''
    if len(departmentChildrent) > 0:
        departmentIds = []
        for de in departmentChildrent:
            departmentIds.append(de.id)
        deString = '(' + ','.join(map(str, departmentIds)) + ')'
        logger.info('===============condition:  %s', deString)
        sql = "SELECT user_name as userName, id FROM mysite_user where user_name like '%s' and department in %s" % ("%%" + condition['userName'] + "%%", deString)
    else:
        sql = "SELECT user_name as userName, id FROM mysite_user where user_name like '%s'" % ("%%" + condition['userName'] + "%%")
    logger.info('===============sql:  %s', sql)
    listUser = User.objects.raw(sql)

    departments = getDepartments()
    context = {
        'listUser': listUser,
        'condition': condition,
        'departments': departments
    }
    return render(request, 'res/listUser.html', context)

def detail(request, userId):
    logger.warning('=============== %d', userId)
    user = get_object_or_404(User, pk=userId)
    datepicker = DatePickerForm(initial={'dateStart': user.birthday})
    departments = Department.objects.raw('SELECT * FROM mysite_department')
    return render(request, 'res/detail.html', {'user': user, 'departments': departments, 'datepicker': datepicker})

def edit(request, userId):
    logger.warning('=============== %d', userId)
    logger.info('==============save user')
    # logger.info('{}', request)
    logger.info('================= %s', request.POST.get('department', 0))
    print(request.POST.get('department', 0))
    user = get_object_or_404(User, pk=userId)
    departments = Department.objects.raw('SELECT * FROM mysite_department')
    
    check = validateUser(request)
    user.user_name = check['user'].user_name
    user.email = check['user'].email
    user.department = check['user'].department
    user.birthday = check['user'].birthday
    logger.info('================= %s', check['validate'])
    logger.info('================= %s', check['error'])    

    if check['validate']:
        user.save()
        return HttpResponseRedirect(reverse('mysite:detail', args=(user.id,)))
    else:
        datepicker = DatePickerForm()
        if user.birthday:
            # set value form
            datepicker = DatePickerForm(initial={'dateStart': user.birthday})
        departments = Department.objects.raw('SELECT * FROM mysite_department')
        logger.info('================= %s', user.user_name)
        logger.info('================= %s', user.email)    
        content = {
            'departments': departments,
            'datepicker': datepicker,
            'error': check['error'],
            'user': user
        }
        logger.info('=================AAAAAAAAAAAAAAAAAAAAAAAAAA') 
        return render(request, 'res/detail.html', content)
        # return render(request, 'res/detail.html', {'user': user, 'departments': departments, 'datepicker': datepicker})
def add(request):
    datepicker = DatePickerForm()
    departments = Department.objects.raw('SELECT * FROM mysite_department')
    content = {
        'departments': departments,
        'datepicker': datepicker,
        'user': User()
    }
    return render(request, 'res/add_user.html', content)
def save(request):
    check = validateUser(request)
    logger.info('================= %s', check['validate'])
    logger.info('================= %s', check['error'])    

    if check['validate']:
        user = check['user']
        user.save()
        logger.info('================= %d', user.pk)
        return HttpResponseRedirect(reverse('mysite:add'))
    else:
        user = check['user']
        datepicker = DatePickerForm()
        if user.birthday:
            # set value form
            datepicker = DatePickerForm(initial={'dateStart':user.birthday})
        departments = Department.objects.raw('SELECT * FROM mysite_department')
        logger.info('================= %s', user.user_name)
        logger.info('================= %s', user.email)    
        content = {
            'departments': departments,
            'datepicker': datepicker,
            'error': check['error'],
            'user': user
        }
        return render(request, 'res/add_user.html', content)

    # return render(request, 'res/add_user.html', content)
def validateUser(request):
    error = {
        'name': '',
        'email': '',
        'dateStart': '',
        'department': ''
    }
    validate = True

    logger.info('================= %s', request.POST.get('name', ''))
    logger.info('================= %s', request.POST.get('email', ''))
    logger.info('================= %s', request.POST.get('dateStart', ''))
    logger.info('================= %s', request.POST.get('department', ''))

    user = User()

    name = request.POST.get('name', '')
    if name == '':
        error['name'] = 'Please input name user'
        validate = False
    elif len(name) > 20 or len(name) < 6:
        error['name'] = 'len 6-20'
        validate = False

    email = request.POST.get('email', '')
    if email == '':
        error['email'] = 'Please input email'
        validate = False
    elif not(re.search(EMAIL_REGEX, email)):
        error['email'] = 'email no match'
        validate = False

    dateStart = request.POST.get('dateStart', '')
    if dateStart == '':
        error['dateStart'] = 'Please select birthday'
        validate = False
    else:
        user.birthday = datetime.datetime.strptime(dateStart, '%m/%d/%Y').date()

    department = request.POST.get('department', '')
    if department == '':
        error['department'] = 'Please select department'
        validate = False
    else:
        user.department = int(department)

    user.user_name = name
    user.email = email

    content = {
        'user': user,
        'validate': validate,
        'error': error
    }
    return content

def getDepartments():
    departments = Department.objects.raw('SELECT * FROM mysite_department')
    departments = list(departments)

    deParents = collections.defaultdict(list)
    for de in departments:
        deParents[de.parent_id].append(de)
    logger.info('=================deParents:  %s', deParents)

    deConverts = []
    for k in deParents:
        convertDepartment(deConverts, k, deParents, 0)

    return deConverts

#  display list depart
def departments(request):
    content = {
        'departments': getDepartments()
    }
    return render(request, 'res/departments.html', content)

def convertDepartment(deConverts, k, deParents, level):
    deChildrents = deParents[k]
    # logger.info('\n=================deChildrent:  %s', deChildrents)
    for deChildrent in deChildrents:
        if deChildrent not in deConverts:
            deChildrent.level = level
            deConverts.append(deChildrent)

            # logger.info('=================deConverts:  %s', deConverts)
            if deChildrent.id in deParents:
                convertDepartment(deConverts, deChildrent.id, deParents, level + 1)

def findDepartmentFromDepartmentParent(deparentIdParent):
    departments = Department.objects.raw('SELECT * FROM mysite_department')
    departments = list(departments)

    deParents = collections.defaultdict(list)
    for de in departments:
        deParents[de.parent_id].append(de)

    deConverts = []
    for k in deParents:
        findDepartmentChildrent(deConverts, k, deParents, deparentIdParent)
    return deConverts
    
def findDepartmentChildrent(deConverts, k, deParents, deparentIdParent):
    deChildrents = deParents[k]
    # logger.info('\n=================deChildrent:  %s', deChildrents)
    for deChildrent in deChildrents:
        if deChildrent not in deConverts:

            if deChildrent.id == deparentIdParent:
                deConverts.append(deChildrent)
                # logger.info('=================deConverts:  %s', deConverts)
                if deChildrent.id in deParents:
                    getDepartmentChildrent(deConverts, deChildrent.id, deParents)
            else:
                if deChildrent.id in deParents:
                    findDepartmentChildrent(deConverts, deChildrent.id, deParents, deparentIdParent)

def getDepartmentChildrent(deConverts, k, deParents):
    deChildrents = deParents[k]
    for deChildrent in deChildrents:
        if deChildrent not in deConverts:
            deConverts.append(deChildrent)
            if deChildrent.id in deParents:
                getDepartmentChildrent(deConverts, deChildrent.id, deParents)

def removeDepartment(request):
    departmentId = int(request.GET.get('departmentId', 0))
    if departmentId <= 0:
        logger.info('============error===========')
    else:
        # get list department childrent
        deChildrents = findDepartmentFromDepartmentParent(departmentId)
        if len(deChildrents) > 0:
            departmentIds = []
            for de in deChildrents:
                departmentIds.append(de.id)
            deString = '(' + ','.join(map(str, departmentIds)) + ')'
            logger.info("===============deString: %s", deString)
            users = User.objects.filter("department=1")
            logger.info("===============users: %s", users)
            # users.update()
            # Department.object.raw("DELETE FROM mysite_user WHERE department in %s" % (deString))
    content = {
        'departments': getDepartments()
    }
    return render(request, 'res/departments.html', content)