
from fmi_xml_parser import *
from fmi_weather_data import *
from excel_reader import *
from data_tools import *
from sklearn import linear_model
import numpy as np

import matplotlib.pyplot as plt

def amain():
    
    dates = []
    visitors = []
    
    for i in range(2, 7):
        data = read_excel("sheets/Kavijatilasto_201"+ str(i) +".xlsx")
        print np.shape(data)
        dates.append(data[:,:8])
        visitors.append(data[:,8])

    X = np.concatenate(dates, axis=0).astype(float)
    Y = np.concatenate(visitors).astype(float)
    
    tt = np.array([1601.77869336, -1.70961991, 1348.80103501])
    
    fig = plt.figure(1)
    ax1 = fig.add_subplot(211)
    ax1.plot(X[:,7], Y)
    
    ax2 = fig.add_subplot(212)
    model_x = np.arange(365)
    model_y = tt[0] * np.sin(tt[1] + 2*np.pi*model_x/365) + tt[2]
    print model_x
    print model_y
    #plt.xlabel('date')
    #plt.ylabel('visitors')
    ax2.plot(model_x, model_y)
    plt.show()

def main():
    
    d_t = ml_dates()
    ml_all(d_t)
    #main_ridge_test()

def main_ridge_test():
    
    w_data = open_data_file("testidata/weather_data_test")
    v_data = open_data_file("testidata/visitor_data_test")
    
    w_clean = w_data[:,3:]
    v_clean = v_data[:,10]
    w_clean = np.delete(w_clean, [4, 11, 18], axis=1)
    print w_clean[:10]
    #print v_clean
    
    
    print len(w_clean)
    X_tr = w_clean[:2554-365]
    Y_tr = v_clean[:2554-365]
    #print len(X_tr)
    
    mask_tr = ~np.isnan(X_tr).any(axis=1)
    X_tr = X_tr[mask_tr]
    Y_tr = Y_tr[mask_tr]
    #print len(X_tr)
    
    X_te = w_clean[2554-365:]
    Y_te = v_clean[2554-365:]
    
    mask_te = ~np.isnan(X_te).any(axis=1)
    
    X_te = X_te[mask_te]
    Y_te = Y_te[mask_te]
    print Y_te
    
    
    reg = linear_model.Ridge (alpha = 1.0)
    reg.fit (X_tr, Y_tr)
    print reg.coef_ 
    Y_predict = reg.predict(X_te)
    
    X = np.arange(len(Y_te))
    
    plt.plot(X, Y_te, color="blue")
    
    plt.plot(X, Y_predict, color="red")
    
    plt.show()
    
    

#
#
#
def gradient_descent_date_only(X, Y, theta, a):
    loss = 100
    k = 0
    while loss > 0 and k < 5000:
        loss = loss_date_only(X, Y, theta)
        print "loss: " + str(loss)
        theta = gradient_step_date_only(X, Y, theta, a)
        print "new_theta: " + str(theta)
        k += 1
        print k
    return theta

def gradient_descent_date(X, Y, theta, a, max_rounds=200):
    loss = 1000000000
    k = 0
    while loss > 150000 and k < max_rounds:
        loss = loss_date(X, Y, theta)
        print "loss: " + str(loss)
        theta = gradient_step_date(X, Y, theta, a)
        print "new_theta: " + str(theta)
        k += 1
        print k
    return theta, loss

def gradient_descent_all(X, Y, theta, a, max_rounds=200):
    loss = 1000000000.0
    prev_loss = loss
    k = 0
    while loss > 15000 and k < max_rounds:
        prev_loss = loss
        loss = loss_all(X, Y, theta)
        print "loss: " + str(loss)
        #~ if loss < prev_loss:
            #~ if (prev_loss - loss) / loss < 0.01:
                #~ a = a*1.2
        #~ else:
            #~ a = a/2
        #if k % 100 == 0:
        #    a = a/1.1
        
        #print "multiplier: " + str(a)
        theta = gradient_step_all(X, Y, theta, a)
        #print "new_theta: " + str(theta)
        k += 1
        print k
    return theta, loss

def loss_date(X, Y, theta):
    n = len(Y)
    err = 0.0
    for i in range(len(Y)):
        x,y = X[i],Y[i]
        err += (y - predict_date(x, theta)) ** 2
    return (1.0/float(n)) * err

def loss_date_only(X, Y, theta):
    n = len(Y)
    err = 0.0
    for i in range(len(Y)):
        err += (Y[i] - (theta[0]*np.exp(-((X[i]-theta[1])**2)/(2*(theta[2]**2))) + theta[3])) ** 2
    return (1.0/float(n)) * err

def loss_all(X, Y, theta):
    n = len(Y)
    err = 0.0
    for i in range(len(Y)):
        x,y = X[i],Y[i]
        err += (y - predict_all(x, theta)) ** 2
    return (1.0/float(n)) * err

def gradient_date_only(X, Y, theta):
    n = len(Y)
    g = [0.0, 0.0, 0.0, 0.0]
    for i in range(n):
        x = X[i]
        y = Y[i]
        g[0] += -2 * np.exp(-((x-theta[1])**2)/(2*(theta[2]**2))) * (y - gauss(x, theta))
        g[1] += -2 * (x - theta[1])/(theta[2]**2) * theta[0] * np.exp(-((x-theta[1])**2)/(2*(theta[2]**2))) * (y - gauss(x, theta))
        g[2] += -2 * ((x - theta[1])**2)/(theta[2]**3) * theta[0] * np.exp(-((x-theta[1])**2)/(2*(theta[2]**2))) * (y - gauss(x, theta))
        g[3] += -2 * (y - gauss(x, theta))
    
    print "gradient: " + str((1.0/float(n)) * np.array(g))
    return (1.0/float(n)) * np.array(g)

def gradient_date(X, Y, theta):
    n = len(Y)
    g = np.zeros(11)
    for i in range(n):
        x,y = X[i],Y[i]
        #inner function
        inner = (y - predict_date(x, theta))
        wk_sum_ = wk_sum(x[:7], theta[:7])
        gauss_ = gauss(x[7], theta[7:11])
        #Derivates for each theta:
        for a in range(7):
            g[a] += -2 * x[a] * gauss_ * inner
        g[7] += -2 * wk_sum_ * np.exp(-((x[7]-theta[1])**2)/(2*(theta[2]**2))) * inner
        g[8] += -2 * wk_sum_ * (x[7] - theta[1])/(theta[2]**2) * theta[0] * np.exp(-((x[7] - theta[1])**2)/(2*(theta[2]**2))) * inner
        g[9] += -2 * wk_sum_ * ((x[7] - theta[1])**2)/(theta[2]**3) * theta[0] * np.exp(-((x[7] - theta[1])**2)/(2*(theta[2]**2))) * inner
        g[10] += -2 * wk_sum_ * inner
    
    #print "gradient: " + str((1.0/float(n)) * g)
    return (1.0/float(n)) * g

def gradient_all(X, Y, theta):
    n = len(Y)
    l = len(theta)
    g = np.zeros(l)
    for i in range(n):
        x,y = X[i],Y[i]
        #inner function
        inner = (y - predict_all(x, theta))
        wk_sum_ = wk_sum(x[:7], theta[:7])
        gauss_ = gauss(x[7], theta[7:11])
        lin_weath_ = lin_weath(x[8:], theta[11:-1])
        #Derivates for each theta:
        for a in range(7):
            g[a] += -2 * x[a] * gauss_ * lin_weath_ * inner
        g[7] += -2 * wk_sum_ * np.exp(-((x[7]-theta[1])**2)/(2*(theta[2]**2))) * lin_weath_ * inner
        g[8] += -2 * wk_sum_ * (x[7] - theta[1])/(theta[2]**2) * theta[0] * np.exp(-((x[7] - theta[1])**2)/(2*(theta[2]**2))) * lin_weath_ * inner
        g[9] += -2 * wk_sum_ * ((x[7] - theta[1])**2)/(theta[2]**3) * theta[0] * np.exp(-((x[7] - theta[1])**2)/(2*(theta[2]**2))) * lin_weath_ * inner
        g[10] += -2 * wk_sum_ * lin_weath_ * inner
        for a in range(11,l-2):
            g[a] += -2 * wk_sum_ * gauss_ * x[a-3] * inner
        g[l-2] += -2 * wk_sum_ * gauss_ * inner
        g[l-1] += -2 * inner
            
    
    #print "gradient: " + str((1.0/float(n)) * g)
    return (1.0/float(n)) * g

def gradient_step_date_only(X, Y, theta, a):
    return theta - a * gradient_date_only(X, Y, theta)

def gradient_step_date(X, Y, theta, a):
    return theta - a * gradient_date(X, Y, theta)
    
def gradient_step_all(X, Y, theta, a):
    return theta - a * gradient_all(X, Y, theta)

#
#   frequently calculated functions
#
def gauss(x, w):
    return (w[0]*np.exp(-((x-w[1])**2)/(2*(w[2]**2))) + w[3])

def wk_sum(x, w):
    return np.sum(w*x)
    
def lin_weath(x, w):
    return np.sum(w[:-1]*x) + w[-1]

#
#   predictions
#
def predict_date(x, theta):
    if type(x[0]) == np.ndarray:
        a = []
        for x_i in x:
            a.append(wk_sum(x_i[:7], theta[:7]) * gauss(x_i[7], theta[7:]))
        return np.array(a)
    else:
        return wk_sum(x[:7], theta[:7]) * gauss(x[7], theta[7:])

def predict_all(x, theta):
    if type(x[0]) == np.ndarray:
        a = []
        for x_i in x:
            #print x_i
            a.append(wk_sum(x_i[:7], theta[:7]) * gauss(x_i[7], theta[7:11]) * lin_weath(x_i[8:], theta[11:-1]) + theta[-1])
        return np.array(a)
    else:
        return wk_sum(x[:7], theta[:7]) * gauss(x[7], theta[7:11]) * lin_weath(x[8:], theta[11:-1]) + theta[-1]

def predict_date_only(x, theta):
    return theta[0]*np.exp(-((x-theta[1])**2)/(2*(theta[2]**2))) + theta[3]

if __name__ == "__main__":
    main()
