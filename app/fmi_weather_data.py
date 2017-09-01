
import os, sys, string, requests
from fmi_xml_parser import *
from data_tools import *



def main():
    
    #request_fmi_data("6a33fb69-82f6-4944-be01-483774407843", "101004", "2017-01-01T12:00:00Z", "2017-01-02T18:00:00Z")
    request_fmi_forecast(get_fmi_code("fmi_code"), "101004", "2017-06-28T12:00:00Z", "2017-06-28T18:00:00Z", "testidata/ennustetesti")
    request_fmi_data(get_fmi_code("fmi_code"), "101004", "2017-06-26T12:00:00Z", "2017-06-26T18:00:00Z", "testidata/havaintotesti")
    
def request_fmi_data(key, station, start_date, end_date, output_file):
    
    req_url = ("http://data.fmi.fi/fmi-apikey/" + key + "/wfs?request=getFeature&storedquery_id=fmi::observations::weather"+
        "::timevaluepair&fmisid=" + station +
        "&starttime=" + start_date +
        "&endtime=" + end_date +
        "&timestep=" + "180" +
        "&parameters=temperature,precipitation1h,windspeedms,totalcloudcover")
        #"&parameters=t2m,r_1h,ws_10min,n_man")
        #"&parameters=t2m,ws_10min,rh,r_1h,snow_aws,vis,n_man")
    
    #print req_url
    
    req = requests.get(req_url)
    print req.status_code
    if req.status_code == 200:
        xml = req.content
        #save_file(xml, "testidata/" + station + "_" + start_date + "_" + end_date + ".txt")
        save_file(xml, output_file)
    else:
        print "FMI API ERROR:"
        print req.content
        raise Exception("FMI API ERROR:" + req.content)


def request_fmi_forecast(key, station, start_date, end_date, output_file=None):
    
    req_url = ("http://data.fmi.fi/fmi-apikey/" + key + "/wfs?request=getFeature&storedquery_id=fmi::forecast::hirlam::surface::point"+
        "::timevaluepair&place=" + "Kumpula" +
        "&starttime=" + start_date +
        "&endtime=" + end_date +
        "&timestep=" + "180" +
        "&parameters=temperature,precipitation1h,windspeedms,totalcloudcover")
    
    #print req_url
    
    req = requests.get(req_url)
    print req.status_code
    if req.status_code == 200:
        xml = req.content
        #save_file(xml, "testidata/" + station + "_" + start_date + "_" + end_date + ".txt")
        if output_file is None:
            return xml
        else:
            save_file(xml, output_file)
    else:
        print "FMI API ERROR:"
        print req.content
        raise Exception("FMI API ERROR:" + req.content)

if __name__ == "__main__":
    main()
