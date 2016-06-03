from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib import messages
from django.conf import settings

from indigo.models import (
    Group,
    User
)
import ldap

from users.forms import UserForm

def notify_agent(user_id, event=""):
    from nodes.client import choose_client
    client = choose_client()
    client.notify(user_id, event)

@login_required
def home(request):
    # TODO: Order by username
    user_objs = list(User.objects.all())

    paginator = Paginator(user_objs, 10)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)

    ctx = {
        "user": request.user,
        "users": users,
        "user_count": len(user_objs)
    }
    return render(request, 'users/index.html', ctx)

def userlogin(request):
    from django.contrib.auth import login

    if request.method == "GET":
        return render(request, 'users/login.html', {})

    errors = ""
    username = request.POST.get('username')
    password = request.POST.get('password')

    invalid = "Username/Password not valid"

    if not username or not password:
        errors = "Username and password are required"

    if not errors:
        user = User.find(username)
        if not user:
            errors = invalid
        else:
            if not user.authenticate(password) and not ldapAuthenticate(username, password):
                errors = invalid

        if not errors:
            request.session['user'] = unicode(user.name)
            return redirect("/")

    ctx = {}
    if errors:
        ctx = {'errors': errors}


    return render(request, 'users/login.html', ctx)

def ldapAuthenticate(username, password):
    if settings.AUTH_LDAP_SERVER_URI is None:
        return False

    if settings.AUTH_LDAP_USER_DN_TEMPLATE is None:
        return False

    try:
        connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        connection.protocol_version = ldap.VERSION3
        user_dn = settings.AUTH_LDAP_USER_DN_TEMPLATE % {"user": username}
        connection.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.SERVER_DOWN:
        # TODO: Return error instead of none
        return False


@login_required
def delete_user(request, name):
    user = User.find(name)
    if not user:
        raise Http404

    if not request.user.administrator:
        raise PermissionDenied

    if request.method == "POST":
        user.delete(username=request.user.name)
        messages.add_message(request, messages.INFO,
                             "The user '{}' has been deleted".format(user.name))
        return redirect('users:home')

    # Requires delete on user
    ctx = {
        "user": user,
    }

    return render(request, 'users/delete.html', ctx)

@login_required
def edit_user(request, name):
    # Requires edit on user
    user = User.find(name)
    if not user:
        raise Http404()

    if not request.user.administrator:
        raise PermissionDenied

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.update(email=data['email'],
                        administrator=data['administrator'],
                        active=data['active'],
                        username=request.user.name)
            if data["password"] != user.password:
                user.update(password=data["password"],
                            username=request.user.name)
            return redirect('users:home')
    else:
        initial_data = {'username': user.name,
                        'email': user.email,
                        'administrator': user.administrator,
                        "active": user.active,
                        "password": user.password
                       }
        form = UserForm(initial=initial_data)

    ctx = {
        "form": form,
        "user": user,
    }

    return render(request, 'users/edit.html', ctx)


@login_required
def new_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.create(name=data.get("username"),
                        # TODO: Check if we can't harmonize unicode use for passwords between django and CLI
                        password=data.get("password").encode("ascii", "ignore"),
                        email=data.get("email", ""),
                        administrator=data.get("administrator", False),
                        active=data.get("active", False),
                        username=request.user.name)
            messages.add_message(request, messages.INFO,
                             "The user '{}' has been created".format(user.name))
            return redirect('users:home')
    else:
        form = UserForm()

    ctx = {
        "form": form,
    }
    return render(request, 'users/new.html', ctx)

def userlogout(request):
    request.session.flush()
    request.user = None
    return render(request, 'users/logout.html', {})

@login_required
def user_view(request, name):
    # argument is the login name, not the uuid in Cassandra
    user = User.find(name)
    if not user:
        return redirect('users:home')
        #raise Http404

    ctx = {
        "req_user": request.user,
        "user_obj": user,
        "groups": [Group.find(gname) for gname in user.groups]
    }
    return render(request, 'users/view.html', ctx)
