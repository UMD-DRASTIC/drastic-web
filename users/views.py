from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    user_objs = User.objects.order_by('username')

    paginator = Paginator(user_objs.all(), 20)
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
        "users": users,
        "user_count": user_objs.count()
    }
    return render(request, 'users/index.html', ctx)

@login_required
def user_view(request, id):
    user_obj = get_object_or_404(User, username=id)

    ctx = {
        "user_obj": user_obj,
    }
    return render(request, 'users/view.html', ctx)