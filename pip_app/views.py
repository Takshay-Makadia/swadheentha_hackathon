from django.http import HttpResponse
from django.template import loader
def home(request):
    return HttpResponse("Hello, Django!")
def navbar(request):
    template = loader.get_template('navbar.html')
    context={

    }
    return HttpResponse(template.render(context,request))
from pip_app.models import User


def login(request):
    template = loader.get_template('login.html')
    authorized = False
    if request.method == "POST":
        print(request.POST)
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_database = User.objects.all()
        for user in user_database:
            if user.email == email:
                if user.password == password:
                    authorized = True
                    context = {
                        'valid': authorized,
                        'message': 'Succesfully Logged in!'
                    }
                    return HttpResponse(template.render(context, request))
                else:
                    context = {
                        'valid': authorized,
                        'message': 'Incorrect Password!'
                    }
                    return HttpResponse(template.render(context, request))
            else:
                context = {
                    'valid': authorized,
                    'message': 'User doesnot exits!'
                }
                return HttpResponse(template.render(context, request))

    context = {
    }
    return HttpResponse(template.render(context, request))

