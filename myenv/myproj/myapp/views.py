from django.http import HttpResponse
from django.template import loader
import datetime


def index(request):
    today = datetime.datetime.now().date()
    template = loader.get_template("appname/index.html")
    context = {"today": today}
    return HttpResponse(template.render(context, request))
