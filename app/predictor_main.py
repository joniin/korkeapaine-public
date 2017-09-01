import numpy as np
from fmi_xml_parser import *
from excel_reader import *
from data_tools import *
from fmi_weather_data import *
from ml import *
from tools import *
from plot import *

def main():
    
    #
    # update things
    #
    update_weather_data(get_path("weather_data"))
    update_visitor_data(get_path("visitor_data"), get_path("sheets_folder"))
    
    
    #
    # learn things
    #
    init_weight_path = get_path("best_init_weights")
    final_weight_path = get_path("best_final_weights")
    
    DX_tr, DY_tr, DX_te, DY_te = load_and_format_visitor_data(get_path("visitor_data"))
    theta_d_init = load_weigths(init_weight_path)[0]
    
    theta_dates, best_date_t_init = learn_dates(DX_tr, DY_tr, DX_te, DY_te, theta_d_init)
    save_weights(best_date_t_init, 0, init_weight_path)
    save_weights(theta_dates, 0, final_weight_path)
    print "Best date weights saved"
    
    theta_dates_final = np.copy(theta_dates)
    
    WX_tr, WY_tr, WX_te, WY_te = load_and_format_all_data(get_path("weather_data"), get_path("visitor_data"))
    theta_w_init = load_weigths(init_weight_path)[1]
    
    theta_all, best_weather_t_init = learn_all(WX_tr, WY_tr, WX_te, WY_te, theta_dates, theta_w_init)
    save_weights(best_weather_t_init, 1, init_weight_path)
    save_weights(theta_all, 1, final_weight_path)
    print "Best weather weights saved"
    
    theta_all_final = np.copy(theta_all)
    
    
    #
    # predict things
    #
    tomorrow_wd = get_tomorrow_date_weekday()
    #print tomorrow_wd
    # data for 12:00 and 18:00 and cloud information removed
    forecast = get_forecast_for_tomorrow()[4:7]
    #print forecast
    
    pred_x = np.append(tomorrow_wd, forecast)
    print "PREDICTION x"
    print pred_x
    
    prediction_date = predict_date(pred_x[:8], theta_dates_final)
    print prediction_date
    
    prediction_all = predict_all(pred_x, theta_all_final)
    print prediction_all
    
    save_predictions(get_path("predictions"), pred_x, prediction_date, prediction_all)
    
    #
    # plot predictions
    #
    predictions = get_predictions(get_path("predictions"))
    visitors = get_visitor_data(get_path("visitor_data"))
    
    combined = combine_visitors_predictions(visitors, predictions)
    print combined
    
    err_date, err_weather = calc_predcition_errs(combined)
    print err_date
    print err_weather
    plot_combined(combined, get_path("fig_all_history"))
    plot_combined(combined, get_path("fig_all_two_weeks"), 14)
    
def load_weigths(path):
    return open_data_file(path)

def save_weights(w, spot, path):
    old = load_weigths(path)
    old[spot] = w
    save_data(old, path)
    

def save_predictions(path, prediction_x, prediction_date, prediction_weather):
    prediction_year = np_date(get_tomorrow())[0]
    prediction_x_with_year = np.append(prediction_year, prediction_x)
    print prediction_x_with_year
    
    full_prediction = np.concatenate((prediction_x_with_year, np.array(["date="+str(prediction_date)]), np.array(["weather="+str(prediction_weather)])))
    print full_prediction
    
    old_predictions = load_predictions(path)
    
    if len(old_predictions) > 0:
        if np.all(prediction_x_with_year[:9] == [float(x) for x in old_predictions[-1][:9]]):
            old_predictions[-1] = full_prediction #replace last
            save_data(old_predictions, path)
            print "Prediction overwritten"
        else:
            print old_predictions
            print full_prediction
            all_predictions = np.concatenate((old_predictions, np.array([full_prediction])), axis=0)
            save_data(all_predictions, path)
            print "Prediction saved"
    else:
        save_data([full_prediction], path)
        print "Prediction saved"
            

def get_forecast_for_tomorrow():
    
    tomorrow = get_tomorrow()
    date_str = tomorrow.strftime("%Y") + "-" + tomorrow.strftime("%m") + "-" + tomorrow.strftime("%d")
    start_time = date_str + "T12:00:00Z"
    end_time = date_str + "T18:00:00Z"
    
    xml_str = request_fmi_forecast(get_fmi_code(get_path("fmi_code")), "101004", start_time, end_time)
    forecast_raw = parse_xml_str(xml_str)
    forecast = format_data(forecast_raw, [12,15,18])[0][3:]
    
    return forecast

def get_tomorrow_date_weekday():
    tomorrow = get_tomorrow()
    weekday = tomorrow.weekday()
    
    np_wdate = np.zeros(8)
    np_wdate[7] = to_simple_date(np_date(tomorrow))[1]
    np_wdate[weekday] += 1
    return np_wdate

def learn_dates(X_tr, Y_tr, X_te, Y_te, theta_init=None):
    gauss_multip = np.array([10000.0, 400.0, 100.0, 300.0])
    
    #
    if theta_init == None:
        theta_init = np.append(np.ones(7), np.random.rand(4) * gauss_multip)
    best_theta_init = theta_init
    best_theta = theta_init
    best_loss = 1000000000000
    
    for i in range(5):
        print "KIERROS " + str(i)
        print theta_init
        
        tt, loss = gradient_descent_date(X_tr, Y_tr, theta_init, 0.000001, 25)
        print "Final loss: " + str(loss)
        
        if loss < best_loss:
            best_loss = loss
            best_theta_init = theta_init
            best_theta = tt
        #new theta_init for next round
        theta_init = np.append(np.ones(7), np.random.rand(4) * gauss_multip)
    
    tt = best_theta
    print "Best loss: " + str(best_loss)
    print "Best init weigths: " + str(best_theta_init)
    print "Best theta: " + str(best_theta)
    
    
    plt.plot(X_te, Y_te, color="blue")
    model_x = X_te #X[:365]
    model_y = predict_date(model_x, tt)
    plt.plot(model_x, model_y, color="red")
    #plt.show()
    plt.savefig(get_path("date_test_fig"))
    plt.clf()
    
    return tt, best_theta_init
    
def learn_all(X_tr, Y_tr, X_te, Y_te, date_theta=None, weather_t_init=None):
    
    if date_theta is None:
        d_t = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1000.0, 200.0, 30.0, 150.0])
    else:
        d_t = date_theta
        d_t[7] = d_t[7]/5
    
    #temp, rain, winds, clouds, +vakio
    if weather_t_init == None:
        weather_t_init = np.random.rand(5)
    best_weather_t_initl = weather_t_init
    best_theta = np.append(d_t, weather_t_init)
    best_loss = 1000000000000
    
    for i in range(5):
        print "KIERROS " + str(i)
        print weather_t_init
        
        t = np.append(np.copy(d_t), weather_t_init)
        tt, loss = gradient_descent_all(X_tr, Y_tr, t, 0.00000002, 25)
        print "Final loss: " + str(loss)
        
        if loss < best_loss:
            best_loss = loss
            best_weather_t_init = weather_t_init
            best_theta = tt
        #new t for next round
        weather_t_init = np.random.rand(5)
    
    tt = best_theta
    print "Best loss: " + str(best_loss)
    print "Best weigths: " + str(best_weather_t_init)
    print "Best theta: " + str(best_theta)
    
    
    
    plt.plot(X_te[:,7], Y_te, color="blue")
    model_y = predict_all(X_te, tt)
    plt.plot(X_te[:,7], model_y, color="red")
    #plt.show()
    plt.savefig(get_path("weather_test_fig"))
    plt.clf()
    
    return tt, best_weather_t_init

def load_and_format_visitor_data(path):
    
    v_data = to_simple_data(open_data_file(path))
    
    X = np.append(v_data[:,2:-1], np.transpose(np.array([v_data[:,1]])), axis=1)
    Y = v_data[:,-1]
    
    X_tr = X[:-365]
    Y_tr = Y[:-365]
    soften_spikes(Y_tr, 10, 10)
    soften_spikes(Y_tr, 5, 5)
    
    X_te = X[-365:]
    Y_te = Y[-365:]
    
    return X_tr, Y_tr, X_te, Y_te

def load_and_format_all_data(weather_path, visitor_path):
    
    w_data = open_data_file(weather_path)
    v_data = open_data_file(visitor_path)
    
    D = combine_data(v_data, w_data)
    # data for 12:00 and 18:00 and cloud information removed
    D = np.delete(D, [8,9,10,11,15,16,17,18,19], axis=1)
    
    D_tr = D[:-365]
    D_te = D[-365:]
    
    D_tr = clean_data(D_tr)
    D_te = clean_data(D_te)
    
    X_tr = D_tr[:,:-1]
    Y_tr = D_tr[:,-1]
    soften_spikes(Y_tr, 10, 10)
    soften_spikes(Y_tr, 5, 5)
    X_te = D_te[:,:-1]
    Y_te = D_te[:,-1]
    
    return X_tr, Y_tr, X_te, Y_te

if __name__ == "__main__":
    main()
