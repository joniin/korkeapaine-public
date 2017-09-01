import numpy as np
import matplotlib.pyplot as plt
from predictor_main import *
from data_tools import *
from tools import *



def main():
    predictions = get_predictions(get_path("predictions"))
    visitors = get_visitor_data(get_path("visitor_data"))
    
    combined = combine_visitors_predictions(visitors, predictions)
    print combined
    
    err_date, err_weather = calc_predcition_errs(combined)
    print err_date
    print err_weather
    plot_combined(combined, get_path("fig_all_history"))


def calc_predcition_errs(combined, last=None):
    if last is not None and last < len(combined):
        combined = combined[-last:]
    
    err_dates = np.abs(1 - (combined[:,-2] / combined[:,-3]))
    err_weathers = np.abs(1- (combined[:,-1] / combined[:,-3]))
    
    return np.average(err_dates), np.average(err_weathers)

def plot_combined(combined, fig_name, last=None):
    
    if last is not None and last < len(combined):
        combined = combined[-last:]
    
    x_ticks = [date_to_str(x) for x in dates_of_X(combined)]
    
    X = np.arange(len(combined))
    Y_real = combined[:,-3]
    Y_date = combined[:,-2]
    Y_weather = combined[:,-1]
    
    real, = plt.plot(X, Y_real, color="black", label="Real visitors")
    date, = plt.plot(X, Y_date, color="red", label="Prediction by date")
    weather, = plt.plot(X, Y_weather, color="green", label="Prediction by weather")
    plt.legend(handles=[real, date, weather])
    plt.ylim([0, 10000])
    plt.xticks(X, x_ticks, rotation="vertical", fontsize=8)
    #plt.show()
    plt.savefig(fig_name, bbox_inches="tight")


def combine_visitors_predictions(visitors, predictions):
    visitor_dates = visitors[:,:9]
    prediction_dates = predictions[:,:9]
    
    #print visitor_dates == prediction_dates
    
    combined = []
    
    for p in range(len(prediction_dates)):
        for v in range(len(visitor_dates)):
            if np.all(prediction_dates[p] == visitor_dates[v]):
                combined.append(np.append(visitors[v], predictions[p][-2:]))
                break
                
    return np.array(combined)


    
if __name__ == "__main__":
    main()
