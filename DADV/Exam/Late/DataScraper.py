import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
from multiprocessing import Pool

url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")

header = soup.find_all('th')
headerList = []
for x in header:
    headerList.append(x.get_text(strip=True))
headerList = headerList[0:9]

d = soup.find('table')

data = []

for row in d.find_all('tr'):
    sampleList = []
    for td in row.find_all('td'):
        sampleList.append(td.get_text(strip=True))
    data.append(sampleList)

data.pop(0)

df = pd.DataFrame(data, columns = headerList)

symbol = df['Symbol']
period1 = "1483228800"
period2 = "1609545600"

def scrape(l):
    link = "https://query1.finance.yahoo.com/v7/finance/download/"+l+"?period1="+period1+"&period2="+period2+"&interval=1wk&events=history&includeAdjustedClose=true"
    response = requests.get(link)
    bytes_io = io.BytesIO(response.content)
    dataframe = pd.read_csv(bytes_io, error_bad_lines=False)
    dataframe['Symbol'] = l
    return dataframe

if __name__ == '__main__':
    p = Pool(30)
    df_list = p.map(scrape,symbol)
    p.close()
    for t in df_list:
        if len(t.columns) > 3:
            close = t['Close'].tolist()
            gl = []
            for i in range(1,len(close)):
                gl.append(((close[i]-close[i-1])/close[i-1])*100)
            gl.insert(0,((gl[0]+gl[1]+gl[2])/3)*100)
            t['Gain or Loss'] = gl

    table = pd.concat(df_list).reset_index(drop=True)

    table.to_csv('Weekly.csv')
