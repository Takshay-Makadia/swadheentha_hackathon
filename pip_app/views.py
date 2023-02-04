from keras.layers import Dense, LSTM
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from pip_app.models import User
from django.http import HttpResponse
from django.template import loader
from pandas_datareader import data as pdr
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
import pandas as pd
import numpy as np
import yfinance as yf

from django.shortcuts import render


yf.pdr_override()
tip_stock_data = [[189.6889966111405, 0.7060766202032482, 'FedEx Corp'],
                  [244.65085540555947, 1.5198581124400334, 'Microsoft'],
                  [95.0167578768742, 0.9917686892076745, 'Amazon'],
                  [105.38846594293318, 0.7523660348394969, 'Google'],
                  [28.653646620252747, 0.13682440490106274, 'Marathon Oil Corp'],
                  [15.58123777522924, 0.0316022962929452, 'American Airline Group'],
                  [249.91836326515798, -1.628491556125482, 'Intuitive Surgical'],
                  [40.20137876987968, -0.0012488189144619355, 'Delta Air Lines'],
                  [386.390697277, 0.6748122246563071, 'Deere & Company'],
                  [15.904774689379396, 0.07756562712530979, 'Newell Brands']]

is_login = False


def home(request):
    template = loader.get_template('home.html')
    context = {}
    return HttpResponse(template.render(context, request))


def login(request):
    template = loader.get_template('login.html')
    authorized = 1
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_database = User.objects.all()
        for user in user_database:
            if user.email == email:
                if user.password == password:
                    global is_login
                    is_login = True
                    return HttpResponseRedirect('/description')
                else:
                    context = {
                        'valid': authorized,
                        'message': 'Incorrect Password!',
                    }
                    return HttpResponse(template.render(context, request))
        context = {
            'valid': authorized,
            'message': 'User doesnot exits!',
        }
        return HttpResponse(template.render(context, request))
    context = {
    }
    return HttpResponse(template.render(context, request))


def logout(request):
    global is_login
    is_login = False
    return HttpResponseRedirect('/login')


def signup(request):
    template = loader.get_template('signup.html')
    authorized = 1
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
                    'valid': authorized,
                    'message': 'User already exist. Use login'
                }
                return HttpResponse(template.render(context, request))

        if user_new.age < '18':
            context = {
                'valid': authorized,
                'message': 'Age less than 18. You cannot use the portal'
            }
            return HttpResponse(template.render(context, request))

        if user_new.password != request.POST.get('cnfPassword'):
            context = {
                'valid': authorized,
                'message': 'Password do not match'
            }
            return HttpResponse(template.render(context, request))

        user_new.save()
        context = {
            'valid': 0,
            'message': 'Sign up successfull'
        }
        return HttpResponseRedirect('login')
    context = {
    }
    return HttpResponse(template.render(context, request))


def description(request):
    if is_login == True:
        global tip_stock_data
        tip_stock_data = modelrunner(tip_stock_data)
        tip_stock_data.sort(reverse=True, key=lambda x: x[1])
        context = {
            'data': tip_stock_data
        }
        return render(request, 'description.html', context)
    else:
        return HttpResponseRedirect('login')


def mutual(request):
    return render(request, 'mutual.html', {})


def modelrunner(tip_stock_data):
    if datetime.now().hour == 16 and datetime.now().minute == 56:
        # tip_stock_data = stockpredict()
        print("IN")

    return tip_stock_data


def stockpredict():
    company_list = ['FDX', 'MSFT', 'AMZN', 'GOOGL',
                    'MRO', 'AAL', 'ISRG', 'DAL', 'DE', 'NWL']
    values_list = []
    error_return = []
    maincompany = ['FedEx Corp', 'Microsoft', 'Amazon', 'Google', 'Marathon Oil Corp',
                   'American Airline Group', 'Intuitive Surgical', 'Delta Air Lines', 'Deere & Company', 'Newell Brands']

    for ylist in company_list:
        df1 = pdr.get_data_yahoo(ylist, start='2018-01-01', end=datetime.now())

        data = df1.filter(['Close'])

        myset = data.values

        training_data_len = int(np.ceil(len(myset) * .95))
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(myset)

        train_data = scaled_data[0:int(training_data_len), :]

        x_train = []
        y_train = []

        for i in range(60, len(train_data)):
            x_train.append(train_data[i-60:i, 0])

            y_train.append(train_data[i, 0])

        x_train, y_train = np.array(x_train), np.array(y_train)

        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        model = Sequential()

        model.add(LSTM(128, return_sequences=True,
                  input_shape=(x_train.shape[1], 1)))

        model.add(LSTM(64, return_sequences=False))
        model.add(Dense(30))

        model.add(Dense(1))

        model.compile(optimizer='adam', loss='mean_squared_error')

        model.fit(x_train, y_train, batch_size=1, epochs=1)
        test_data = scaled_data[training_data_len - 60:, :]
        x_test = []
        for i in range(60, len(test_data)):
            x_test.append(test_data[i-60:i, 0])

        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        predictionstoday = model.predict(x_test)
        predictionstoday = predictionstoday.tolist()
        predictionstoday = scaler.inverse_transform(predictionstoday)
        values_list.append(predictionstoday[59].tolist()[0])
        profit = (predictionstoday[59]-predictionstoday[58]).tolist()[0]
        error_return.append(profit)
    ret_data = []
    for i in range(0, 10):
        ret_data.append([values_list[i], error_return[i], maincompany[i]])
    return ret_data
