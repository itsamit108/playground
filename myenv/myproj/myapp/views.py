from django.shortcuts import render
import datetime


def index(request):
    today = datetime.datetime.now().date()
    days = [1, 2, 3, 4, 5]  # just an example list of days
    context = {"today": today, "days": days}
    return render(request, "myapp/index.html", context)
