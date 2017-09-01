import datetime
import numpy as np
import os
from collections import defaultdict

def main():
    #file_len_over_0("testidata/predictions")
    
    
    pass

def get_path(name, path_file="paths"):
    paths = defaultdict(lambda: "path not found")
    #yes yes I know, this is stupid way and results many unnecessary I/O operations
    with open(path_file, "r") as f:
        for line in f:
            ll = line.split(": ")
            paths[ll[0]] = ll[1].rstrip()
    
    return paths[name]
    

def get_yesterday():
    return datetime.datetime.now() - datetime.timedelta(days=1)

def get_today():
    return datetime.datetime.now()

def get_tomorrow():
    return datetime.datetime.now() + datetime.timedelta(days=1)
    
def np_date(date_obj):
    return np.array([float(date_obj.strftime("%Y")), float(date_obj.strftime("%m")), float(date_obj.strftime("%d"))])

def is_file_empty(path):
    return os.stat(path).st_size == 0
            
def date_to_str(np_date):
    return str(int(np_date[2])) + "." + str(int(np_date[1])) + "." + str(int(np_date[0]))

def dates_of_X(X):
    dates = np.concatenate((np.array([X[:,0]]).T, np.array([X[:,8]]).T), axis=1)
    return np.array([to_complex_day(x) for x in dates])

def to_simple_date(day_c):
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return np.array([day_c[0], day_c[2] + sum(month_days[:int(day_c[1])-1])])
    
def to_complex_day(day_s):
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    m = 0
    d = day_s[1] - month_days[m]
    
    while d > 0:
        m += 1
        d -= month_days[m]
    
    return np.array([day_s[0], float(m+1), d + month_days[m]])

if __name__ == "__main__":
    main()
