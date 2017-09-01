from fmi_weather_data import request_fmi_data
from fmi_xml_parser import *
from excel_reader import *
from tools import *
import numpy as np
import os.path
import time
import urllib

def main():
    update_weather_data(get_path("weather_data"))
    update_visitor_data(get_path("visitor_data"), get_path("sheets_folder"))

def update_weather_data(path):
    update_done = False
    
    while not update_done:
        time.sleep(1)
        if os.path.isfile(path): 
            old_data = open_data_file(path)
            start_time, end_time = get_update_interval_strs(old_data[-1][:3])
        else:
            old_data = None
            start_time, end_time = get_update_interval_strs(np.array([2009.0, 12.0, 31.0]))
        
        if start_time is None:
            print "Weather data up-to-date"
            update_done = True
            return
        
        xml_tmp = get_path("xml_tmp")
        request_fmi_data(get_fmi_code(get_path("fmi_code")), "101004", start_time, end_time, xml_tmp)
        
        new_data_raw = parse_xml_file(xml_tmp)
        #save_data(data, "testidata/testi")
        new_data = format_data(new_data_raw, [12,15,18])
        #save_data(f_data, "testidata/testi_f")
        
        if old_data is None:
            save_data(new_data, path)
        else:
            save_data(np.concatenate([old_data, new_data]), path)
        print "Weather data updated from " + start_time + " to " + end_time
    
def open_data_file(path, s=False):
    data = []
    with open(path, "r") as f:
        for line in f:
            if s:
                data.append([str(x).rstrip() for x in line.split(" ")])
            else:
                data.append([float(x) for x in line.split(" ")])
    return np.array(data)

def combine_data(v_data, w_data):
    w_d = w_data[:,3:]
    v_d = to_simple_data(v_data)
    
    #TODO: tarkistus etta samat paivat
    
    #w_d = np.delete(w_d, [4, 11, 18], axis=1)
    #print w_d[:10]
    l_v = len(v_d[0])
    D = np.append(v_d[:,2:-1], np.transpose(np.array([v_d[:,1]])), axis=1)
    D = np.append(D, w_d, axis=1)
    D = np.append(D, np.transpose(np.array([v_d[:,-1]])), axis=1)
    
    #print D[0]
    return D

def clean_data(data):
    mask_nan = ~np.isnan(data).any(axis=1)
    data = data[mask_nan]    
    return data



def soften_spikes(v_data, threshold=5, divider=2):
    for i in range(1,len(v_data)-1):
        if v_data[i] > threshold*v_data[i+1] and v_data[i] > threshold*v_data[i-1]:
            v_data[i] = v_data[i] / divider
    if v_data[0] > threshold* v_data[1]:
        v_data[0] = v_data[0] / divider
    if v_data[-1] > threshold* v_data[-2]:
        v_data[-1] = v_data[-1] / divider

def to_simple_data(data, k=0):
    simple = []
    
    for row in data:
        if k > 0:
            simple.append(row[0:k] + to_simple_date(row[k:k+3]) + row[k+3:])
        else:
            simple.append(to_simple_date(row[k:k+3]).tolist() + row[k+3:].tolist())
        
    return np.array(simple)
        

def get_update_interval_strs(last_day):
    if is_yesterday(last_day):
        return None, None
    
    return get_time_str(add_days(last_day, 1), 12), get_time_str(add_days(last_day, 7), 18)

def add_days(day_c, k, limit_yesterday=True):
    last_s = to_simple_date(day_c)
    if int(day_c[1]) == 2 and day_c[2] > 21:
        last_s[1] += max(k-1, 1)
    else:
        last_s[1] += k
    
    if last_s[1] > 365:
        last_s[0] += 1
        last_s[1] -= 365
    
    candidate = to_complex_day(last_s)
    
    if limit_yesterday:
        yesterday = np_date(get_yesterday())
        if candidate[0] > yesterday[0]:
            return yesterday
        elif candidate[0] == yesterday[0] and candidate[1] > yesterday[1]:
            return yesterday
        elif candidate[0] == yesterday[0] and candidate[1] == yesterday[1] and candidate[2] > yesterday[2]:
            return yesterday
    
    return candidate
    
def get_time_str(day_c, hours):
    #2017-01-01T12:00:00Z
    s = (str(int(day_c[0])) + "-" +
        (str(int(day_c[1])) if day_c[1] > 9 else "0" + str(int(day_c[1]))) + "-" +
        (str(int(day_c[2])) if day_c[2] > 9 else "0" + str(int(day_c[2]))) + "T" +
        (str(int(hours)) if hours > 9 else "0" + str(int(hours))) + ":00:00Z")
    return s
    
def is_yesterday(last_day):
    return np.all(last_day == np_date(get_yesterday()))

def update_visitor_data(path, sheets_folder):
    current_year = int(datetime.datetime.now().strftime("%y"))
    
    visitors = open_data_file(get_path("visitor_data"))
    last_visitors_date = visitors[-1][:3]
    yesterday = np_date(get_yesterday())
    
    if len(visitors) < 1 or not np.all(last_visitors_date == yesterday):
        update_excel_sheets(sheets_folder, current_year)
        
        print "parsing visitor excel data.."
        datas = []
        for i in range(10, current_year):
            datas.append(read_excel(sheets_folder + "/visitors_20" +str(i)+ ".xlsx", 2000+i))
        
        datas.append(read_excel_current(sheets_folder + "/visitors_current.xlsx"))
        
        save_data(np.concatenate(datas), path)
    print "Visitor data up-to-date"

def update_excel_sheets(folder, current_year):
    url_file = "visitor_count_locations"
    visitor_urls = get_visitor_urls(url_file)
    
    testfile = urllib.URLopener()
    
    
    for i in range(10, current_year):
        #print visitor_urls["20" + str(i)]
        if not os.path.isfile(folder + "/visitors_20"+str(i)+".xlsx"):
            testfile.retrieve(visitor_urls["20" + str(i)], folder + "/visitors_20"+str(i)+".xlsx")
            print "visitors_20" + str(i) + " retrieved"
    
    #uusin tulee aina paivittaa TODO: paitsi jos tanaan jo paivitetty
    #if not os.path.isfile(folder + "/visitors_current"+".xlsx"):
    testfile.retrieve(visitor_urls["current"], folder + "/visitors_current.xlsx")
    print "visitors_current" + " retrieved"

def get_visitor_urls(path):
    year_urls = {}
    with open(path, "r") as url_file:
        for line in url_file:
            yu = [x.rstrip() for x in line.split(" ")]
            year_urls[yu[0]] = yu[1]
    return year_urls

def get_fmi_code(path):
    with open(path, "r") as f:
        code = f.read().rstrip()
    return code

def get_predictions(path):
    pred_data = load_predictions(path)
    date_data = pred_data[:,:9].astype(float)
    date_predictions = np.array([[x.replace("date=", "") for x in pred_data[:,-2]]]).astype(float)
    weather_predictions = np.array([[x.replace("weather=", "") for x in pred_data[:,-1]]]).astype(float)
    #print date_data
    #print date_predictions
    #print weather_predictions
    predictions = np.concatenate((date_data, date_predictions.T, weather_predictions.T), axis=1)
    #print predictions
    return predictions

def get_visitor_data(path):
    v_data = to_simple_data(open_data_file(path))
    #reordering because some previous fucking logic...
    years = np.array([v_data[:,0]])
    days = np.array([v_data[:,1]])
    weeks = v_data[:,2:9]
    visitors = np.array([v_data[:,-1]])
    
    visitor_data = np.concatenate((years.T, weeks, days.T, visitors.T), axis=1)
    #print visitor_data[-5:]
    return visitor_data

def load_predictions(path):
    return open_data_file(path, True)



if __name__ == "__main__":
    main()
