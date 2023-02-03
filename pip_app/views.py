from pip_app.models import User
from django.http import HttpResponse
from django.template import loader


def home(request):
    return HttpResponse("Hello, Django!")


def login(request):
    template = loader.get_template('login.html')
    authorized = False
    if request.method == "POST":
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


def signup(request):
    template = loader.get_template('signup.html')
    if request.method == "POST":
        user_new = User(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            age=request.POST.get('age'),
            password=request.POST.get('password'))

        user_database = User.objects.all()
        for user in user_database:
            if user.email == user_new.email:
                context = {
                    'message': 'User already exist. Use login'
                }
                return HttpResponse(template.render(context, request))

        if user_new.age < '18':
            context = {
                'message': 'Age less than 18. You cannot use the portal'
            }
            return HttpResponse(template.render(context, request))

        if user_new.password != request.POST.get('cnfPassword'):
            context = {
                'message': 'Password do not match'
            }
            return HttpResponse(template.render(context, request))

        user_new.save()
    context = {
        'message': 'Sign up successfull'
    }
    return HttpResponse(template.render(context, request))
