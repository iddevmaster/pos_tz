from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.db.models import Count
from ..models import category_program_permission,user_detail
from ..constant import defaultTitle, api_id_card

def login(request):
    title = defaultTitle
    context = {'title': title}
    if request.user.id is not None:
        return redirect("/")
    return render(request, 'login.html', context)


def login_check(request):
    username = request.POST['username']
    password = request.POST['password']
    print("The original date is : ",username)
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect("/")
    else:
        messages.error(
            request, "Invalid Credentials Error With Correct Username/Password")
        return redirect("/login")


def logout(request):
    auth.logout(request)
    return redirect("/login")


def manual_idcard(request):
    user_id = request.user.id
    # Menu
    try:
        u = user_detail.objects.get(user_id=user_id)
        cm_id = u.cm
    except user_detail.DoesNotExist:
        cm_id = 0
    listMenuPermission = category_program_permission.objects.filter(cm_id=cm_id).values(
        "group_value", "group_label").annotate(dcount=Count('group_value')).order_by("group_label")
    objMenu = []
    for rs in list(listMenuPermission):
        children = category_program_permission.objects.filter(
            cm_id=cm_id, group_value=rs['group_value']).order_by("page_label")
        r = {'group_label': rs['group_label'],
             'group_value': rs['group_value'], 'children': children}
        objMenu.append(r)
    context = {'title': defaultTitle, 'api_id_card': api_id_card, 'listMenuPermission': objMenu}
    return render(request, 'general/maual_idcard.html', context)

def handler404(request, exception):
    return render(request, '404.html')
