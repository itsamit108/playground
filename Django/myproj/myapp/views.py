from django.shortcuts import render, HttpResponse

# Create your views here.


def page1(request):
    return HttpResponse("Hello World")
