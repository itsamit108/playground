from django.shortcuts import render, HttpResponse

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def about(request):
    return HttpResponse("This is the about page.")
