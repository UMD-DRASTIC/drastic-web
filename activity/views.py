from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from indigo.models.activity import Activity

@login_required
def home(request):
    activities = Activity.recent(10)
    return render(request, 'activity/index.html', {'activities': activities})