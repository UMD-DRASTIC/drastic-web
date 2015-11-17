

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
def add_user(request, id):
    group = Group.find_by_id(id)
    if not group:
        raise Http404
    if not request.user.administrator:
        raise PermissionDenied
    users = [(u.name, u.name) for u in User.objects.all()
             if not group.id in u.groups]
    if request.method == 'POST':
        form = GroupAddForm(users, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            added = []
            for username in data.get('users', []):
                user = User.find(username)
                if user:
                    if id not in user.groups:
                        user.groups.append(id)
                        user.update(groups=user.groups)
                        notify_agent(group.id, "group:add:{}".format(user.name))
                        added.append("'{}'".format(user.name))
            if added:
                msg = "{} has been added to the group '{}'".format(", ".join(added),
                                                                   group.name)
            else:
                msg = "No user has been added to the group '{}'".format(group.name)
            messages.add_message(request, messages.INFO, msg)
            return redirect('groups:view', id=id)
            
    else:
        form = GroupAddForm(users)

    ctx = {
        "group": group,
        "form": form,
        "users": users
    }
    return render(request, 'groups/add.html', ctx)


@login_required
def delete_group(request, id):
    group = Group.find_by_id(id)
    if not group:
        raise Http404
    if not request.user.administrator:
        raise PermissionDenied
    if request.method == "POST":
        group.delete()
        messages.add_message(request, messages.INFO,
                             "The group '{}' has been deleted".format(group.name))
        notify_agent(group.id, "groups:delete")
        return redirect('groups:home')

    # Requires delete on user
    ctx = {
        "group": group,
    }
    return render(request, 'groups/delete.html', ctx)


@login_required
def edit_group(request, id):
    # Requires edit on user
    group = Group.find(id)
    if not group:
        raise Http404()

    if not request.user.administrator:
        raise PermissionDenied

    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            group.update(name=data['name'])
            notify_agent(group.id, "group:edit")
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
def group_view(request, id):
    # argument is the uuid in Cassandra
    group = Group.find_by_id(id)
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
            group = Group.create(name=data.get("name"))
            notify_agent(group.id, "groups:new")
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
def rm_user(request, id, uname):
    group = Group.find_by_id(id)
    user = User.find(uname)
    if not request.user.administrator:
        raise PermissionDenied
    if user and group:
        if group.id in user.groups:
            user.groups.remove(group.id)
            user.update(groups=user.groups)
            notify_agent(group.id, "group:rm:{}".format(user.name))
            msg = "{} has been removed fromthe group '{}'".format(user.name,
                                                                   group.name)
            messages.add_message(request, messages.INFO, msg)
    else:
        raise Http404
    return redirect('groups:view', id=id)