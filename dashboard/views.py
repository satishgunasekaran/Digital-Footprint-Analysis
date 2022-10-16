from urllib import request
from django.shortcuts import render
from datetime import datetime
from .models import Posts

# from .models import Posts

def dashboard(request):
    all_posts = Posts.objects.all()
    return render(request, 'dashboard/dashboard.html', {'today': datetime.today(),'posts':all_posts})

def refreshdata(request):
    
    return render(request, 'dashboard/dashboard.html', {'today': datetime.today()})