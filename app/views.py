from app import app
from flask import render_template
from code import *
from plot import *
from data_tools import *
import numpy as np
import os

@app.route('/')
@app.route('/index')
def index():
    time = {'now': str(get_time())}
    
    print os.listdir(".")
    
    predictions = get_predictions(get_path("predictions"))
    visitors = get_visitor_data(get_path("visitor_data"))
    
    combined = combine_visitors_predictions(visitors, predictions)
    #print combined
    
    
    err_date, err_weather = calc_predcition_errs(combined)
    err_date_14, err_weather_14 = calc_predcition_errs(combined)
    
    last_w_predictions = last_weather_predictions(predictions)
    last_d_predictions = last_date_predictions(predictions)
    last_real_value = int(visitors[-1][-1])
    
    
    return render_template('index.html',
                           title='Home',
                           time=time,
                           predictions_w=last_w_predictions,
                           predictions_d=last_d_predictions,
                           real=last_real_value,
                           err_date=int(100*(1.0-err_date)),
                           err_date_14=int(100*(1.0-err_date_14)),
                           err_weather=int(100*(1.0-err_weather)),
                           err_weather_14=int(100*(1.0-err_weather_14)))



def last_weather_predictions(predictions):
    #return [int(x) for x in predictions[-3:,-1]]
    
    last = ["failed to predict"] * 3
    tomorrow = np_date(get_tomorrow())
    today = np_date(get_today())
    yesterday = np_date(get_yesterday())
    
    
    last_dates = dates_of_X(predictions[-3:])
    last_all = np.concatenate((last_dates, np.array([predictions[-3:,-1]]).T), axis=1)
    
    
    for p in last_all:
        if np.all(p[:3] == yesterday):
            last[0] = int(p[-1])
        if np.all(p[:3] == today):
            last[1] = int(p[-1])
        if np.all(p[:3] == tomorrow):
            last[2] = int(p[-1])
    
    return last
    
def last_date_predictions(predictions):
    #return [int(x) for x in predictions[-3:,-2]]
    
    last = ["failed to predict"] * 3
    tomorrow = np_date(get_tomorrow())
    today = np_date(get_today())
    yesterday = np_date(get_yesterday())
    
    print np.array([predictions[-3:,0]]).T
    print np.array([predictions[-3:,8]]).T
    print "nakki"
    
    last_dates = dates_of_X(predictions[-3:])
    last_all = np.concatenate((last_dates, np.array([predictions[-3:,-2]]).T), axis=1)
    
    
    for p in last_all:
        if np.all(p[:3] == yesterday):
            last[0] = int(p[-1])
        if np.all(p[:3] == today):
            last[1] = int(p[-1])
        if np.all(p[:3] == tomorrow):
            last[2] = int(p[-1])
    
    return last
