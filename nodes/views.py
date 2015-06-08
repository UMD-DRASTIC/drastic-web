from django.shortcuts import render
from django.core.urlresolvers  import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import NodeForm
from .client import NodeClient

import uuid
import datetime

@login_required
def home(request):

    # TODO: Fix me by looking up actual data.
    nodes = []
    for x in range(1, 8):
        nodes.append(
        {
            "id": str(uuid.uuid4()),
            "name": "Test node %s" % x,
            "address": "192.168.10.1%s" % x,
            "last_contact": datetime.datetime.now(),
            "status": "up"
        })

    nodes[2]['status'] = 'unknown'
    nodes[5]['status'] = 'down'


    return render(request, 'nodes/index.html', {"nodes": nodes})

@login_required
def new(request):
    form = NodeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            messages.add_message(request, messages.INFO, 'New node was added')
            return HttpResponseRedirect(reverse('nodes:home'))

    return render(request, 'nodes/new.html', {'form': form})


@login_required
def edit(request, id):
    initial_data = {
        "id": "id",
        "name": "Editing ...",
        "address": "192.168.0.1"
    }

    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            messages.add_message(request, messages.INFO, 'Node information has been changed')
            print "Message!"
            return HttpResponseRedirect(reverse('nodes:home'))
    else:
        form = NodeForm(initial=initial_data)

    return render(request, 'nodes/edit.html', {'form': form})

@login_required
def check(request, id):
    # TODO: Get the node details
    address = "192.168.10.111"

    client = NodeClient(address)
    ok, metrics = client.get_state()
    if ok:
        messages.add_message(request, messages.INFO, 'The node was reachable')
    else:
        messages.add_message(request, messages.WARNING, 'The node at {} was unreachable'.format(address))
    return HttpResponseRedirect(reverse("nodes:home"))

