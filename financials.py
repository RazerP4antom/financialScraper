from datetime import datetime
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd
from scraper import ticker

def get_page(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'close',
        'DNT': '1', # Do Not Track Request Header 
        'Pragma': 'no-cache',
        'Referrer': 'https://google.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }

    return requests.get(url, headers=headers)


def parse_rows(table_rows):
    parsed_rows = []

    for table_row in table_rows:
        parsed_row = []
        el = table_row.xpath("./div")

        none_count = 0

        for rs in el:
            try:
                (text,) = rs.xpath('.//span/text()[1]')
                parsed_row.append(text)
            except ValueError:
                parsed_row.append(np.NaN)
                none_count += 1

        if (none_count < 4):
            parsed_rows.append(parsed_row)
            
    return pd.DataFrame(parsed_rows)


def clean_data(df):
    df = df.set_index(0) 
    df = df.transpose() 
    
    cols = list(df.columns)
    cols[0] = 'Date'
    df = df.set_axis(cols, axis='columns', copy=False)
    
    numeric_columns = list(df.columns)[1::] # Take all columns, except the first (which is the 'Date' column)

    for column_index in range(1, len(df.columns)): # Take all columns, except the first (which is the 'Date' column)
        # df.iloc[:,column_index] = df.iloc[:,column_index].str.replace(',', '') # Remove the thousands separator
        df[df.columns[column_index]] = df[df.columns[column_index]].str.replace(',', '')
        df[df.columns[column_index]] = df[df.columns[column_index]].astype(np.float64)
        
    return df


def scrape_table(url):
    page = get_page(url)

    tree = html.fromstring(page.content)
    table_rows = tree.xpath("//div[contains(@class, 'D(tbr)')]")
    
    assert len(table_rows) > 0
    
    df = parse_rows(table_rows)
    df = clean_data(df)
        
    return df


df_balance_sheet = scrape_table('https://finance.yahoo.com/quote/' + ticker + '/balance-sheet?p=' + ticker)
df_balance_sheet.to_excel('BalanceSheet.xlsx', index=False)

df_income_statement = scrape_table('https://finance.yahoo.com/quote/' + ticker + '/financials?p=' + ticker)
df_income_statement.to_excel('IncomeStatement.xlsx', index=False)

df_cash_flow = scrape_table('https://finance.yahoo.com/quote/' + ticker + '/cash-flow?p=' + ticker)
df_cash_flow.to_excel('CashFlow.xlsx', index=False)