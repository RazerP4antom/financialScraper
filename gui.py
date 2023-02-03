import tkinter as tk
from tkinter import *
# import jovian
# jovian.commit(project="yahoo-finance-web-scraper")
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sentiment import *
from scraper import *
import numpy as np

BASE_URL = 'https://finance.yahoo.com' #Global Variable
ticker_df = pd.read_csv("constituents_csv.csv")

########## PYTHON FUNTIONS ###############


"""Download a webpage and return a beautiful soup doc"""
def get_page(url):
    response = requests.get(url)
    # print("Works")
    if not response.ok:
        print('Status code:', response.status_code)
        raise Exception('Failed to load page {}'.format(url))
    page_content = response.text
    doc = BeautifulSoup(page_content, 'html.parser')
    return doc


"""Get the list of tags containing news information"""
def get_news_tags(doc):
    news_class = "Ov(h) Pend(44px) Pstart(25px)" ## class name of div tag 
    news_list  = doc.find_all('div', {'class': news_class})
    return news_list



"""Get the news data point and return dictionary"""
def parse_news(news_tag):
    news_source = news_tag.find('div').text #source
    news_headline = news_tag.find('a').text #heading
    news_url = news_tag.find('a')['href'] #link
    news_content = news_tag.find('p').text #content
    news_image = news_tag.findParent().find('img')['src'] #thumb image
    return {'headline' : news_headline,
            'url' : BASE_URL + news_url
           }


"""Get the yahoo finance market news and write them to CSV file """
def scrape_yahoo_news(url):
    # if path is None:
        # path = 'stock-market-news.csv'
        
    # print('Requesting html page')
    doc = get_page(url)

    # print('Extracting news tags')
    news_list = get_news_tags(doc)

    # print('Parsing news tags')
    news_data = [parse_news(news_tag) for news_tag in news_list]

    # print('Save the data to a CSV')
    news_df = pd.DataFrame(news_data)
    news_df.to_csv("stock-market-news.csv", index=None)
    
    #This return statement is optional, we are doing this just analyze the final output 
    return news_df 


'''Checking the input company name/ticker with our list'''
def check_company_ticker(n):
    company_tick = n
    cap_company = n.capitalize()
    cap_tick = company_tick.upper()

    result_ticker = ticker_df[ticker_df["Symbol"] == cap_tick]
    result_company = ticker_df[ticker_df["Name"] == cap_company]

    if not result_company.empty:
        ticker_list = result_company["Symbol"].to_list()
    elif not result_ticker.empty:
        ticker_list = result_ticker["Symbol"].to_list()
    else:
        print("No matching records found")
    
    ticker = str(ticker_list[0])

    return ticker
    


################# TKINTER PART #####################

#display function 
def clicked():
    result = company.get()
    ticker = check_company_ticker(result)
    YAHOO_NEWS_URL = BASE_URL + "/quote/" + ticker + "?p=" + ticker + "&.tsrc=fin-srch"
    news_df = scrape_yahoo_news(YAHOO_NEWS_URL)
    sentences = news_df['headline'].to_list()
    df = pd.DataFrame(columns=['compound', 'neg', 'neu', 'pos'])

    analyzer = SentimentIntensityAnalyzer()
    for sentence in sentences:
        vs = analyzer.polarity_scores(sentence)
        df.loc[len(df)] = [vs['compound'], vs['neg'], vs['neu'], vs['pos']]

    news_df['Sentiment Score'] = df['compound']
    news_df["Sentiment"] = np.where(news_df['Sentiment Score'] >= 0, 'Positive or Neutral', 'Negative')


    n_rows = news_df.shape[0]
    n_cols = news_df.shape[1]

    column_name = news_df.columns
    i = 0
    for j, col in enumerate(column_name):
        text = Text(root, width=40, height=3, bg= "#9BC2E6")
        text.grid(row=i+2, column=j)
        text.insert(INSERT, col)
    
    for i in range(n_rows):
        for j in range(n_cols):
            text = Text(root, width=40, height=3, wrap="word")
            text.grid(row=i+3, column=j)
            text.insert(INSERT, news_df.loc[i][j])


#create window
root = tk.Tk()

#set title and window dimension
root.title("Finsnap")
root.geometry('1920x1080')

#label to root window
lb1 = Label(root, text = "Enter name company name or ticker: ")
lb1.grid()

#adding entry field
company = Entry(root, width=10)
company.grid(column=1, row=0)

#button widget
btn = Button(root, text="Submit", fg= "red", command=clicked)
btn.grid(column=2,row=0)


root.mainloop()
