
import xml.etree.ElementTree as ET
import sys
import numpy as np

def main():
    print sys.argv[1]
    
    data = parse_xml_file(sys.argv[1])
    #save_data(data, "testidata/testi")
    f_data = format_data(data, [12, 15, 18])
    save_data(f_data, "testidata/testi_f")

def parse_xml_str(xml):
    root = ET.fromstring(xml)
    return parse_xml(root)
    
def parse_xml_file(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return parse_xml(root)
    
def parse_xml(root):
    
    data = []
    
    measurement_elems = root.findall(".//{http://www.opengis.net/waterml/2.0}MeasurementTimeseries")
    #print measurement_elems
    
    #time stamps
    ms_times = [ms_time_elem.text for ms_time_elem in measurement_elems[0].findall(".//{http://www.opengis.net/waterml/2.0}time")]
    data.append(["time"] + ms_times)
    
    for ms_elem in measurement_elems:
        ms_elem_id = ms_elem.attrib.get("{http://www.opengis.net/gml/3.2}id")
        #print ms_elem_id
        #ms_times = [ms_time_elem.text for ms_time_elem in ms_elem.findall(".//{http://www.opengis.net/waterml/2.0}time")]
        ms_values = [ms_time_elem.text for ms_time_elem in ms_elem.findall(".//{http://www.opengis.net/waterml/2.0}value")]
        #print ms_times
        #print ms_values
        data.append([ms_elem_id] + ms_values)
        
    data_np = np.array(data)
    data_t = np.transpose(data_np)
    #print data_t
    return data_t

def format_data(data, times):
    formatted_data = []
    single_day_data = None
    prev_date = None
    
    for row in data[1:]:    #first row is header
        date, time = format_date_time(row[0])
        if date is None:
            continue
        if time not in times:
            continue
        if prev_date == date:
            single_day_data += row[1:].tolist()
        else:
            if single_day_data is not None:
                formatted_data.append(single_day_data)
            single_day_data = date + row[1:].tolist()
        prev_date = date
        
    formatted_data.append(single_day_data)
    
    return np.array(formatted_data, dtype=float)

def format_date_time(s):
    date_s = s[:s.find("T")]
    time = int(s[s.find("T")+1:s.find(":")])
    
    year = int(date_s[:date_s.find("-")])
    month = int(date_s[date_s.find("-")+1:date_s.rfind("-")])
    day = int(date_s[date_s.rfind("-")+1:])
    
    if month == 2 and day == 29:
        return None, None
    
    #print str(year) + "." + str(month) + "." + str(day) + " " + str(time)
    return [year, month, day], time


def save_file(cont, path):
    xml_file = open(path, "w")
    xml_file.write(cont)
    xml_file.close()

def save_data(data, path):
    rows = [" ".join([str(x) for x in row]) for row in data]
    cont_str = "\n".join(rows)
    
    data_file = open(path, "w")
    data_file.write(cont_str)
    data_file.close()


if __name__ == "__main__":
    main()
