from django.http import HttpResponse
from django.template import loader
from pip_app.models import User

def home(request):
    template = loader.get_template('home.html')
    context={}
    return HttpResponse(template.render(context,request))




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
                    'message': 'User does not exits!'
                }
                return HttpResponse(template.render(context, request))

    context = {
    }
    return HttpResponse(template.render(context, request))

