from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import multiprocessing
from multiprocessing import Pool
import threading
import time

start_time = time.time()
url = "https://www.bseindia.com/corporates/List_Scrips.aspx"
segment = "Equity"
status = "Active"


def scrape(driver):
    global df_list
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    header = soup.find_all('th')
    headerList = []
    for x in header:
        headerList.append(x.get_text(strip=True))

    rows = soup.find_all('div',{"class": "col-lg-12 largetable"})[0]
    rows = rows.find_all('tr')
    trList = []
    size = 1
    for var in rows:
        if (size >= 7 and size <= 31 and len(var.get_text()) > 50):
            trList.append(var)
        size += 1

    data = []
    for row in trList:
        sampleList = []
        for td in row.find_all('td'):
            sampleList.append(td.get_text(strip=True))
        data.append(sampleList)

    df = pd.DataFrame(data, columns = headerList)
    return df

def BSE(num):
    l = []
    driver = webdriver.Chrome()
    driver.get(url)
    
    segmentVar = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_ddSegment"]')
    segmentVar.send_keys(segment)

    
    statusVar = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_ddlStatus"]')
    statusVar.send_keys(status)

    submit = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnSubmit"]')
    submit.click()
    
    totalNum = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_trData"]/td').text
    totalNum = int(totalNum.split()[-1])

    for i in range(1,int(totalNum/10)+1):
        next = 0
        page = 0
        if i == 1:
            next = 11
            page = num
        else:
            next = 13
            page = num + 2
        if num == 1:
            l.append(scrape(driver))
            driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td['+str(next)+']/a').click()
        else:
            driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td['+str(page)+']/a').click()
            l.append(scrape(driver))
            driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td['+str(next)+']/a').click()

    if  num <= (totalNum-(int(totalNum/10)*10)) and num == 1:
        l.append(scrape(driver))
    elif num <= (totalNum-(int(totalNum/10)*10)):
        driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td['+str(page+3)+']/a').click()
        l.append(scrape(driver))
    driver.quit()
    return l


if __name__ == '__main__':
    p = Pool(3)
    data = p.map(BSE,range(1,11))
    p.close()
    end_time = time.time()
    df_list = []
    for i in data:
        for j in i:
            df_list.append(j)
    dataframe = pd.concat(df_list, ignore_index=True).reset_index(drop=True)
    dataframe = dataframe.sort_values(by=['Security Code']).reset_index(drop = True)
    # print(dataframe)
    dataframe.to_csv('BSE_Index.csv')
    print(end_time-start_time)

