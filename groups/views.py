

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from groups.forms import (
    GroupForm,
    GroupAddForm
)
from indigo.models import (
    Group,
    User
)


@login_required
def add_user(request, uuid):
    group = Group.find_by_uuid(uuid)
    if not group:
        raise Http404
    if not request.user.administrator:
        raise PermissionDenied
    users = [(u.name, u.name) for u in User.objects.all()
             if not group.uuid in u.groups]
    if request.method == 'POST':
        form = GroupAddForm(users, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            added = []
            for username in data.get('users', []):
                user = User.find(username)
                if user:
                    if uuid not in user.groups:
                        user.groups.append(uuid)
                        user.update(groups=user.groups)
                        added.append("'{}'".format(user.name))
            if added:
                msg = "{} has been added to the group '{}'".format(", ".join(added),
                                                                   group.name)
                group.update(user_uuid=request.user.uuid)
            else:
                msg = "No user has been added to the group '{}'".format(group.name)
            messages.add_message(request, messages.INFO, msg)
            return redirect('groups:view', uuid=uuid)
            
    else:
        form = GroupAddForm(users)

    ctx = {
        "group": group,
        "form": form,
        "users": users
    }
    return render(request, 'groups/add.html', ctx)


@login_required
def delete_group(request, uuid):
    group = Group.find_by_uuid(uuid)
    if not group:
        raise Http404
    if not request.user.administrator:
        raise PermissionDenied
    if request.method == "POST":
        group.delete(user_uuid=request.user.uuid)
        messages.add_message(request, messages.INFO,
                             "The group '{}' has been deleted".format(group.name))
        return redirect('groups:home')

    # Requires delete on user
    ctx = {
        "group": group,
    }
    return render(request, 'groups/delete.html', ctx)


@login_required
def edit_group(request, uuid):
    # Requires edit on user
    group = Group.find(uuid)
    if not group:
        raise Http404()

    if not request.user.administrator:
        raise PermissionDenied

    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            group.update(name=data['name'],
                         user_uuid=request.user.uuid)
            return redirect('groups:home')
    else:
        initial_data = {'name': group.name}
        form = GroupForm(initial=initial_data)

    ctx = {
        "form": form,
        "group": group,
    }

    return render(request, 'groups/edit.html', ctx)


@login_required
def group_view(request, uuid):
    # argument is the uuid in Cassandra
    group = Group.find_by_uuid(uuid)
    ctx = {
        "user": request.user,
        "group_obj": group,
        "members": group.get_usernames()
    }
    return render(request, 'groups/view.html', ctx)


@login_required
def home(request):
    # TODO: Order by groupname
    group_objs = list(Group.objects.all())

    paginator = Paginator(group_objs, 10)
    page = request.GET.get('page')
    try:
        groups = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        groups = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        groups = paginator.page(paginator.num_pages)

    ctx = {
        "user": request.user,
        "groups": groups,
        "group_count": len(group_objs)
    }
    return render(request, 'groups/index.html', ctx)


@login_required
def new_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            group = Group.create(name=data.get("name"),
                                 user_uuid=request.user.uuid)
            messages.add_message(request, messages.INFO,
                             "The group '{}' has been created".format(group.name))
            return redirect('groups:home')
    else:
        form = GroupForm()
    ctx = {
        "form": form,
    }
    
    return render(request, 'groups/new.html', ctx)


def notify_agent(user_id, event=""):
    from nodes.client import choose_client
    client = choose_client()
    client.notify(user_id, event)


@login_required
def rm_user(request, uuid, uname):
    group = Group.find_by_uuid(uuid)
    user = User.find(uname)
    if not request.user.administrator:
        raise PermissionDenied
    if user and group:
        if group.uuid in user.groups:
            user.groups.remove(group.uuid)
            user.update(groups=user.groups)
            group.update(user_uuid=request.user.uuid)
            msg = "{} has been removed fromthe group '{}'".format(user.name,
                                                                   group.name)
            messages.add_message(request, messages.INFO, msg)
    else:
        raise Http404
    return redirect('groups:view', uuid=uuid)