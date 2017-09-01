# -*- coding: UTF-8 -*-

# Function for retrieving data via FMI open data API
# P. Kolari 9/2015
#
# Function arguments:
# personal api-key
# station id (6-digit code)
# type of observations, e.g. weather, weather::daily, radiation
# start date yyyy-mm-dd
# end date yyyy-mm-dd
# output directory (optional, if omitted result file(s) are saved in current working directory)
#
# Usage example:
# python getfmidata.py [your apikey] 101317 weather 2015-02-23 2015-02-24 /data/fmidata/tmp

import os,sys,string,requests
import xml.etree.ElementTree as ET

def parser(item1,item2):
    return item1.text,item2.text

def parse_timeseries(series):
#    return [parser(item1,item2) for item1,item2 in zip(series.iter(tag='{http://www.opengis.net/waterml/2.0}time'),series.iter(tag='{http://www.opengis.net/waterml/2.0}value'))]
# fix for python 2.6 and lower
    return [parser(item1,item2) for item1,item2 in zip(series.getiterator(tag='{http://www.opengis.net/waterml/2.0}time'),series.getiterator(tag='{http://www.opengis.net/waterml/2.0}value'))]

def parse_varnames(series):
    return [item1.attrib.get('{http://www.opengis.net/gml/3.2}id') for item1 in series]

def get_data(apikey,station,obs,firstdate,lastdate):
    url='http://data.fmi.fi/fmi-apikey/' + apikey + '/wfs?request=getFeature&storedquery_id=fmi::observations::' + obs + '::timevaluepair&fmisid=' + station + '&starttime=' + firstdate + '&endtime=' + lastdate
#    url='http://data.fmi.fi/fmi-apikey/' + apikey + '/wfs?request=getFeature&storedquery_id=fmi::observations::' + obs + '::timevaluepair&place=' + station + '&starttime=' + firstdate + '&endtime=' + lastdate
#    print(url)
    print url
    req=requests.get(url)
    dataa=[]
    hdrrow=[]
    if req.status_code==200:
        xmlstring=req.content
        #print xmlstring
        datatree=ET.ElementTree(ET.fromstring(xmlstring))
#        hdrrow=parse_varnames(datatree.iter(tag='{http://www.opengis.net/waterml/2.0}MeasurementTimeseries'))
# fix for python 2.6 and lower
        hdrrow=parse_varnames(datatree.getiterator(tag='{http://www.opengis.net/waterml/2.0}MeasurementTimeseries'))
#        dataa=zip(*(parse_timeseries(series) for series in datatree.iter(tag='{http://www.opengis.net/waterml/2.0}MeasurementTimeseries')))
# fix for python 2.6 and lower
        dataa=zip(*(parse_timeseries(series) for series in datatree.getiterator(tag='{http://www.opengis.net/waterml/2.0}MeasurementTimeseries')))
    return hdrrow,dataa

try:
    scriptname,apikey,station,obs,firstdate,lastdate,outdir=sys.argv
except ValueError:
    apikey=sys.argv[1]
    station=sys.argv[2]
    obs=sys.argv[3]
    firstdate=sys.argv[4]
    lastdate=sys.argv[5]
    outdir=os.path.dirname(os.path.abspath(__file__))
print(' ')
hdrrow,dataa=get_data(apikey,station,obs,firstdate,lastdate)
if len(dataa)>0:
#    stationstr=station.replace('ä','a').replace('ö','o')
    stationstr=station
    outfile=os.path.join(outdir, 'FMI_' + stationstr + '_' + obs.replace(':','') + '_' + firstdate + '_' + lastdate + '.txt')
    f=open(outfile,'w')
#    f.write('datetime ' + ' '.join(hdrrow) + '\n')
    f.write('yy mm dd HH MM SS ' + ' '.join(hdrrow) + '\n')
    ll=len(dataa[0])
    for i in range(0,len(dataa)):
	 # format time stamp
        tmp=dataa[i][0][0]
        tmp=tmp.replace('-',' ').replace('T',' ').replace(':',' ').replace('Z','')
        f.write(tmp)
        for j in range(0,ll):
            f.write(' ' + dataa[i][j][1])
        f.write('\n')
    f.close()
    print('Data written to ' + outfile)
else:
    print('No data.')
