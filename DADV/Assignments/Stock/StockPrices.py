import pandas as pd
from selenium import webdriver
import time
from bs4 import BeautifulSoup
start_time = time.time()
df = pd.read_csv('BSE_Index.csv')
df = df.drop(df.columns[[0]], axis=1)
df.sort_values(['Security Code'], inplace = True)

url = 'https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?flag=0'

driver = webdriver.Chrome()
driver.get(url) 


yearClick = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_rdbYearly"]')
year = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_cmbYearly"]')


yeardict = {}
closedict = {}

yearClick.click()
year.send_keys('2016')

for code in df['Security Code']:
    securitycode = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_smartSearch"]')
    securitycode.clear()
    securitycode.send_keys(code)#524459
    driver.find_element_by_xpath('//*[@id="ulSearchQuote2"]/li').click()
    submit = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnSubmit"]')
    submit.click()

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    trhtml = soup.find_all('tr')[13]

    if len(soup.find_all('tr')) > 15 and driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_lblScripCodeValue"]').text == str(code):
        tdhtml = trhtml.find_all('td')
        yearlist = []
        closelist = []
        for i in range(15, len(tdhtml), 13):
            yearlist.append(tdhtml[i].get_text())
            closelist.append(tdhtml[i+4].get_text())
        yeardict[code] = yearlist
        closedict[code] = closelist
end_time = time.time()
print(yeardict)
print(closedict)
print(end_time-start_time)
