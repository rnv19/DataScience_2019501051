import pandas as pd
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from multiprocessing import Pool

start_time = time.time()
df = pd.read_csv('BSE_Index.csv')
df = df.drop(df.columns[[0]], axis=1)
df.sort_values(['Security Code'], inplace = True)

codesplit = df['Security Code']
iterable = [codesplit[0:1500],codesplit[1500:3000],codesplit[3000:]]
# iterable = [codesplit[0:1],codesplit[1:2],codesplit[2:3]]
url = 'https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?flag=0'

def scrape(l):

    driver = webdriver.Chrome()
    driver.get(url)


    monthClick = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_divDMY"]/table/tbody/tr[2]/td[1]/label')
    month = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_cmbMonthly"]')
    year = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_cmbMYear"]')


    monthdict = {}
    closedict = {}

    monthClick.click()
    month.send_keys('Jul')
    year.send_keys('2020')
    
    for code in l:
        securitycode = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_smartSearch"]')
        securitycode.clear()
        securitycode.send_keys(code)
        driver.find_element_by_xpath('//*[@id="ulSearchQuote2"]/li').click()
        submit = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnSubmit"]')
        submit.click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        trhtml = soup.find_all('tr')[13]
    
        if len(soup.find_all('tr')) > 15 and driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_lblScripCodeValue"]').text == str(code):
            tdhtml = trhtml.find_all('td')
            monthlist = []
            closelist = []
            for i in range(14, len(tdhtml), 12):
                monthlist.append(tdhtml[i].get_text())
                closelist.append(tdhtml[i+4].get_text())
            monthdict[code] = monthlist
            closedict[code] = closelist
        else:
            monthdict[code] = ['Jul 20', 'Aug 20', 'Sep 20', 'Oct 20', 'Nov 20', 'Dec 20', 'Jan 21']
            closedict[code] = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
    driver.quit()
    return [monthdict,closedict]

if __name__ == '__main__':
    p = Pool(3)
    data = p.map(scrape,iterable)
    p.close()

    data[0][0].update(data[1][0])
    data[0][0].update(data[2][0])
    monthdict = data[0][0]   

    data[0][1].update(data[1][1])
    data[0][1].update(data[2][1])
    closedict = data[0][1]

    dataframe = pd.DataFrame(columns=['Security Code','Close Jul 20','Close Aug 20','Close Sep 20','Close Oct 20','Close Nov 20', 'Close Dec 20', 'Close Jan 21'])

    for key in monthdict.keys():
        scode = key
        jul = aug = sep = oct = nov = dec = jan = 'NA'
        mlist = monthdict[key]
        clist = closedict[key]
        for i in range(len(mlist)):
            if mlist[i] == 'Jul 20':
                jul = clist[i]
            elif mlist[i] == 'Aug 20':
                aug = clist[i]
            elif mlist[i] == 'Sep 20':
                sep = clist[i]
            elif mlist[i] == 'Oct 20':
                oct = clist[i]
            elif mlist[i] == 'Nov 20':
                nov = clist[i]
            elif mlist[i] == 'Dec 20':
                dec = clist[i]
            else:
                jan = clist[i]
        d = {'Security Code' : scode, 'Close Jul 20' : jul, 'Close Aug 20' : aug, 'Close Sep 20' : sep, 'Close Oct 20' : oct, 'Close Nov 20' : nov, 'Close Dec 20' : dec, 'Close Jan 21' : jan}
        dataframe = dataframe.append(d, ignore_index=True)
    dataframe.sort_values(by=['Security Code'], inplace = True)
    dataframe = dataframe.reset_index(drop=True)
    dataframe.to_csv('Sample.csv')
    df = pd.merge(df,dataframe,on='Security Code')
    df.to_csv('Output.csv')
    end_time = time.time()
    print(df)
    print(end_time-start_time)
