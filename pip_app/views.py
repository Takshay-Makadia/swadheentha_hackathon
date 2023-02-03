from django.http import HttpResponse
from django.template import loader

def home(request):
    return HttpResponse("Hello, Django!")
def navbar(request):
    template = loader.get_template('navbar.html')
    context={

    }
    return HttpResponse(template.render(context,request))