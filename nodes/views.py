import uuid
import datetime

from django.shortcuts import render
from django.core.urlresolvers  import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import NodeForm
from .client import NodeClient

from indigo.models import Node
from indigo.models.errors import UniqueException


@login_required
def home(request):
    nodes = [n.to_dict() for n in Node.list()]
    return render(request, 'nodes/index.html', {"nodes": nodes})

@login_required
def new(request):
    form = NodeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                Node.create(name=form.cleaned_data["name"],
                            address=form.cleaned_data["address"])
                messages.add_message(request, messages.INFO, 'New node was added')
            except UniqueException:
                messages.add_message(request, messages.ERROR, 'That name is already in use')

            return HttpResponseRedirect(reverse('nodes:home'))

    return render(request, 'nodes/new.html', {'form': form})


@login_required
def edit(request, id):
    # TODO: Create the initial_data from the node itself, if we can
    # find it.
    node = Node.find_by_id(id)
    initial_data = node.to_dict()

    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            node.update(name=form.cleaned_data['name'], address=form.cleaned_data['address'])
            messages.add_message(request, messages.INFO,
                                 "Node information for '{}' has been changed".format(form.cleaned_data['name']))
            return HttpResponseRedirect(reverse('nodes:home'))
    else:
        form = NodeForm(initial=initial_data)

    return render(request, 'nodes/edit.html', {'form': form})

@login_required
def check(request, id):
    node = Node.find_by_id(id)

    client = NodeClient(node.address)
    ok, metrics = client.get_state()
    if ok:
        messages.add_message(request, messages.INFO, 'The node was reachable')
    else:
        messages.add_message(request, messages.WARNING, 'The node at {} was unreachable'.format(node.address))
        node.update(status="DOWN", last_update=datetime.datetime.now())
    return HttpResponseRedirect(reverse("nodes:home"))


@login_required
def logview(request, id):
    # TODO: Get log details for an actual node.....
    node =         {
            "id": str(uuid.uuid4()),
            "name": "Test node 1",
            "address": "192.168.10.12",
            "last_contact": datetime.datetime.now(),
            "status": "up"
        }
    return render(request, 'nodes/logs.html', { "node": node})
