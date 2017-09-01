import numpy as np
import xlrd
import datetime

def main():
    
    data = read_excel_current("sheets/visitors_current.xlsx")
    print data

def read_excel(path, year):
    workbook = xlrd.open_workbook(path)
    return iterate_months(workbook, year)

def read_excel_current(path):
    workbook = xlrd.open_workbook(path)
    return iterate_months_current(workbook)

def iterate_months(workbook, year):
    year_data = []
    for m in range(1, 13):
        year_data += iterate_days(workbook, m, year)
    
    return np.array(year_data)

def iterate_months_current(workbook):
    year_data = []
    current_month = int(datetime.datetime.now().strftime("%m"))
    current_year = int(datetime.datetime.now().strftime("%Y"))
    
    for m in range(1, current_month+1):
        year_data += iterate_days_current(workbook, m, current_year)
    
    return np.array(year_data)

def iterate_days(workbook, m, year):
    sheet_name = "Yht" + str(m)
    
    sheet = workbook.sheet_by_name(sheet_name)
    y = 3
    date_pos = 0
    wk_day_pos = 1
    count_pos = 29
    
    month_data = []
    
    wk_days = {"ma": 0, "ti": 1, "ke": 2, "to": 3, "pe": 4, "la": 5, "su": 6}
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] #forced to filter out 29th of february
    
    #while(sheet.cell(y, date_pos).value != xlrd.empty_cell.value):
    #data format: [date, mo, tu, we, th, fr, sa, su, visitors]
    for d in range(1, month_days[m-1]+1):
        date = int(sheet.cell(d+y, date_pos).value) + sum(month_days[:m-1])
        weekday = wk_days[sheet.cell(d+y, wk_day_pos).value]
        visitors = int(sheet.cell(d+y, count_pos).value)
        
        #day_data = [0,0,0,0,0,0,0, date, visitors] #data and visitors
        day_data = [year,m,d,0,0,0,0,0,0,0, visitors] #data and visitors
        day_data[weekday+3] = 1            #weekday
        
        #print day_data
        
        month_data.append(day_data)
        
    return month_data

def iterate_days_current(workbook, m, year):
    sheet = workbook.sheet_by_index(m-1)
    y = 4
    date_pos = 0
    wk_day_pos = 1
    count_pos = 3
    
    month_data = []
    
    wk_days = {"ma": 0, "ti": 1, "ke": 2, "to": 3, "pe": 4, "la": 5, "su": 6}
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] #forced to filter out 29th of february
    
    
    for d in range(1, month_days[m-1]+1):
        date = int(sheet.cell(d+y, date_pos).value) + sum(month_days[:m-1])
        weekday = wk_days[sheet.cell(d+y, wk_day_pos).value]
        try:
            visitors = int(sheet.cell(d+y, count_pos).value)
        except ValueError:
             break
        
        #day_data = [0,0,0,0,0,0,0, date, visitors] #data and visitors
        day_data = [year,m,d,0,0,0,0,0,0,0, visitors] #data and visitors
        day_data[weekday+3] = 1            #weekday
        
        #print day_data
        
        month_data.append(day_data)
        
    return month_data

if __name__ == "__main__":
    main()
