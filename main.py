from bs4 import BeautifulSoup
import requests
import sqlite3
import re

conn = sqlite3.connect('scraped.db')
curs = conn.cursor()

curs.execute(''' CREATE TABLE CATEGORY(Id INTEGER PRIMARY KEY,NAME TEXT)''')
curs.execute(''' CREATE TABLE BOOKS(Category_Id INTEGER, NAME TEXT,PRICE INTEGER,RATING TEXT)''')

html_content = requests.get('http://books.toscrape.com')
soup = BeautifulSoup(html_content.content)

url = "http://books.toscrape.com/"


def getURLs(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    return (soup)


def getBooks(url):
    soup = getURLs(url)
    # remove the index.html part of the base url before returning the results
    return (["/".join(url.split("/")[:-1]) + "/" + x.find("div").find("a").get('href') for x in
             soup.findAll("article", attrs={"class": "product_pod"})])


pages_urls = []
new_page = "http://books.toscrape.com/catalogue/page-1.html"

while requests.get(new_page).status_code == 200:
    pages_urls.append(new_page)
    new_page = pages_urls[-1].split("-")[0] + "-" + str(int(pages_urls[-1].split("-")[1].split(".")[0]) + 1) + ".html"

booksURLs = []
for page in pages_urls:
    booksURLs.extend(getBooks(page))

names = []
prices = []
rate = []
for x in range(len(booksURLs)):
    soup = getURLs(url)
    all_articles = soup.find_all("article", attrs={"class": "product_pod"})

    for article in all_articles:
        names.append(soup.find("article", class_=("product_pod")).find("h3").get_text())
        prices.append(soup.find("p", class_="price_color").text[2:])  # get rid of the pound sign
        rate.append(soup.find("article", class_=("product_pod")).find('p').get('class')[1])

        curs.execute("INSERT INTO BOOKS VALUES(?,?,?,?)", (x, names, prices, rate))

conn.commit()
conn.close()