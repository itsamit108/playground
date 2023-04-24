import datetime
from django.shortcuts import render


def index(request):
    today = datetime.datetime.now().date()
    context = {"today": today}
    return render(request, "myapp/index.html", context)
