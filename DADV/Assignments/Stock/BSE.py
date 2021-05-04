from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

start_time = time.time()

url = "https://www.bseindia.com/corporates/List_Scrips.aspx"

driver = webdriver.Chrome()
driver.get(url)

segment = "Equity"
segmentVar = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_ddSegment"]')
segmentVar.send_keys(segment)

status = "Active"
statusVar = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_ddlStatus"]')
statusVar.send_keys(status)

submit = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnSubmit"]')
submit.click()


def scrape():
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
# df = scrape()

# driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td[11]/a').click()
totalNum = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_trData"]/td').text
totalNum = int(totalNum.split()[-1])

df = scrape()

for i in range(1,int(totalNum/10)+1):
    start = 0
    end = 0
    next = 0
    if i == 1:
        start = 2
        end = 11
        next = 11
    else:
        start = 4
        end = 13
        next = 13
    for j in range(start, end):
        driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td['+str(j)+']/a').click()
        dataframe = scrape()
        df = pd.concat([df, dataframe], axis=0)
    driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td['+str(next)+']/a').click()
    dataframe = scrape()
    df = pd.concat([df, dataframe], axis=0)

for j in range(5, totalNum-(int(totalNum/10)*10)+4):
    driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_gvData"]/tbody/tr[1]/td/table/tbody/tr/td['+str(j)+']/a').click()
    dataframe = scrape()
    df = pd.concat([df, dataframe], axis=0)
print(df)
end_time = time.time()
print(end_time-start_time)