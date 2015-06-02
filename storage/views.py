from django.shortcuts import render
from django.core.urlresolvers  import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .forms import StorageForm

@login_required
def home(request):
    return render(request, 'storage/index.html', {})

@login_required
def new(request):
    form = StorageForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            return HttpResponseRedirect(reverse('storage:home'))

    return render(request, 'storage/new.html', {'form': form})

@login_required
def modify(request, name):
    return render(request, 'storage/modify.html', {})