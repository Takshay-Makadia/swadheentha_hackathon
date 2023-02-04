from keras.layers import Dense, LSTM
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from pip_app.models import User
from django.http import HttpResponse
from django.template import loader
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf

yf.pdr_override()

def home(request):
    template = loader.get_template('home.html')
    context={}
    return HttpResponse(template.render(context,request))

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
                    tip_stock_data = []
                    context = {
                        'valid': authorized,
                        'message': 'Succesfully Logged in!',
                        'data': tip_stock_data
                    }
                    template = loader.get_template('home.html')
                    return HttpResponse(template.render(context, request))
                else:
                    context = {
                        'valid': authorized,
                        'message': 'Incorrect Password!',
                        'data': []
                    }
                    return HttpResponse(template.render(context, request))
            else:
                context = {
                    'valid': authorized,
                    'message': 'User doesnot exits!',
                    'data': []
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

        predictionstoday = scaler.inverse_transform(predictionstoday)
        values_list.append(predictionstoday[59])

        profit = predictionstoday[59]-predictionstoday[58]
        error_return.append(profit)
    return values_list, error_return, maincompany
