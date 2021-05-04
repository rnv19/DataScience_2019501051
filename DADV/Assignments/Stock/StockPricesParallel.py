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
url = 'https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?flag=0'

def scrape(l):

    driver = webdriver.Chrome()
    driver.get(url)


    yearClick = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_rdbYearly"]')
    year = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_cmbYearly"]')


    yeardict = {}
    closedict = {}

    yearClick.click()
    year.send_keys('2016')
    
    for code in l:
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
        else:
            yeardict[code] = ['2016', '2017', '2018', '2019', '2020', '2021']
            closedict[code] = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']
    driver.quit()
    return [yeardict,closedict]

if __name__ == '__main__':
    p = Pool(3)
    data = p.map(scrape,iterable)
    p.close()

    data[0][0].update(data[1][0])
    data[0][0].update(data[2][0])
    # data[0][0].update(data[3][0])
    # data[0][0].update(data[4][0])
    yeardict = data[0][0]   

    data[0][1].update(data[1][1])
    data[0][1].update(data[2][1])
    # data[0][1].update(data[3][1])
    # data[0][1].update(data[4][1])
    closedict = data[0][1]

    dataframe = pd.DataFrame(columns=['Security Code','Close 2016','Close 2017','Close 2018','Close 2019','Close 2020', 'Close 2021'])

    for key in yeardict.keys():
        scode = key
        c16 = c17 = c18 = c19 = c20 = c21 = 'NA'
        ylist = yeardict[key]
        clist = closedict[key]
        for i in range(len(ylist)):
            if ylist[i] == '2016':
                c16 = clist[i]
            elif ylist[i] == '2017':
                c17 = clist[i]
            elif ylist[i] == '2018':
                c18 = clist[i]
            elif ylist[i] == '2019':
                c19 = clist[i]
            elif ylist[i] == '2020':
                c20 = clist[i]
            else:
                c21 = clist[i]
        d = {'Security Code' : scode, 'Close 2016' : c16, 'Close 2017' : c17, 'Close 2018' : c18, 'Close 2019' : c19, 'Close 2020' : c20, 'Close 2021' : c21}
        dataframe = dataframe.append(d, ignore_index=True)
    dataframe.sort_values(by=['Security Code'], inplace = True)
    dataframe = dataframe.reset_index(drop=True)
    dataframe.to_csv('Sample.csv')
    # df['Close 2016'] = dataframe['Close 2016']
    # df['Close 2017'] = dataframe['Close 2017']
    # df['Close 2018'] = dataframe['Close 2018']
    # df['Close 2019'] = dataframe['Close 2019']
    # df['Close 2020'] = dataframe['Close 2020']
    df = pd.merge(df,dataframe,on='Security Code')
    df.to_csv('Output.csv')
    end_time = time.time()
    print(df)
    print(end_time-start_time)
