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

#display function 
def clicked():
    result = company.get()
    ticker = check_company_ticker(result)
    YAHOO_NEWS_URL = BASE_URL + "/quote/" + ticker + "?p=" + ticker + "&.tsrc=fin-srch"
    news_df = scrape_yahoo_news(YAHOO_NEWS_URL)
    sentences = news_df['content'].to_list()
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
        text = Text(root, width=40, height=1, bg= "#9BC2E6")
        text.grid(row=i+2, column=j)
        text.insert(INSERT, col)
    
    for i in range(n_rows):
        for j in range(n_cols):
            text = Text(root, width=40, height=4, wrap="word")
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
