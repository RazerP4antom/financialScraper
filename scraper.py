import jovian
jovian.commit(project="yahoo-finance-web-scraper")

import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

BASE_URL = 'https://finance.yahoo.com' #Global Variable 


def get_page(url):
    """Download a webpage and return a beautiful soup doc"""
    response = requests.get(url)
    # print("Works")
    if not response.ok:
        print('Status code:', response.status_code)
        raise Exception('Failed to load page {}'.format(url))
    page_content = response.text
    doc = BeautifulSoup(page_content, 'html.parser')
    return doc

def get_news_tags(doc):
    """Get the list of tags containing news information"""
    news_class = "Ov(h) Pend(44px) Pstart(25px)" ## class name of div tag 
    news_list  = doc.find_all('div', {'class': news_class})
    return news_list

def parse_news(news_tag):
    """Get the news data point and return dictionary"""
    news_source = news_tag.find('div').text #source
    news_headline = news_tag.find('a').text #heading
    news_url = news_tag.find('a')['href'] #link
    news_content = news_tag.find('p').text #content
    news_image = news_tag.findParent().find('img')['src'] #thumb image
    return { 'source' : news_source,
            'headline' : news_headline,
            'url' : BASE_URL + news_url,
            'content' : news_content,
            'image' : news_image
           }

def scrape_yahoo_news(url, path=None):
    """Get the yahoo finance market news and write them to CSV file """
    if path is None:
        path = 'stock-market-news.csv'
        
    print('Requesting html page')
    doc = get_page(url)

    print('Extracting news tags')
    news_list = get_news_tags(doc)

    print('Parsing news tags')
    news_data = [parse_news(news_tag) for news_tag in news_list]

    print('Save the data to a CSV')
    news_df = pd.DataFrame(news_data)
    news_df.to_csv(path, index=None)
    
    #This return statement is optional, we are doing this just analyze the final output 
    return news_df 


ticker_df = pd.read_csv("constituents_csv.csv")
company = input("Enter name of the company to find: ")
company_tick = company
cap_company = company.capitalize()
cap_tick = company_tick.upper()

result_ticker= ticker_df[ticker_df["Symbol"] == cap_tick]
result_company = ticker_df[ticker_df["Name"] == cap_company]

if not result_ticker.empty:
    ticker_list = result_ticker["Symbol"].to_list()
elif not result_company.empty:
    ticker_list = result_company["Symbol"].to_list()
else:
    print("No matching records found")

ticker = str(ticker_list[0])

YAHOO_NEWS_URL = BASE_URL + "/quote/" + ticker + "?p=" + ticker + "&.tsrc=fin-srch"
news_df = scrape_yahoo_news(YAHOO_NEWS_URL)