from django.shortcuts import render, HttpResponse

# Create your views here.


def index(request):
    context = {"variable": "This is a string"}
    return render(request, "index.html", context)


def about(request):
    return HttpResponse("About Page")


def services(request):
    return HttpResponse("Services Page")


def contact(request):
    return HttpResponse("Contact Page")
