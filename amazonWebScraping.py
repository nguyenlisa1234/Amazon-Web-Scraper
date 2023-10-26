from lib2to3.pgen2.pgen import DFAState
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import argparse


my_parser = argparse.ArgumentParser(description="Return Daily Amazon Deals")
my_parser.add_argument("searchterm", metavar="searchterm", type=str, help= "The item to be searched for. Use + for spaces.")
args = my_parser.parse_args()


searchterm = args.searchterm


s = HTMLSession()
dealslist = []


url = f"https://www.amazon.com/s?k={searchterm}&i=todays-deals"


def getdata(url):
    r = s.get(url)
    r.html.render(sleep=1)
    soup = BeautifulSoup(r.html.html, "html.parser")
    return soup


def getdeals(soup):
    products = soup.find_all("div", {"data-component-type": "s-search-result"})
    for item in products:
        title = item.find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"}).text.strip()
        short_title = item.find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"}).text.strip()[:25]
        link = item.find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})["href"]
        try:
            saleprice = float(item.find_all("span", {"class": "a-offscreen"})[0].text.replace("$","").replace(",","").strip())
            originalprice = float(item.find_all("span", {"class": "a-offscreen"})[1].text.replace("$","").replace(",","").strip())
        except:
            originalprice = float(item.find("span", {"class": "a-offscreen"}).text.replace("$","").replace(",","").replace(",","").strip())
        try:
            reviews = float(item.find("span", {"class": "a-size-base s-underline-text"}).replace(",","").text.strip())
        except:
            reviews = 0

        saleitem = {
            "title": title,
            "short_title": short_title,
            "link": link,
            "saleprice": saleprice,
            "originalprice": originalprice,
            "reviews": reviews
            }
        dealslist.append(saleitem)


def getnextpage(soup):
    pages = soup.find("span", {"class": "s-pagination-strip"}) # this is for the strip that has the page numbers
    if not pages.find("span", {"class": "s-pagination-item s-pagination-next s-pagination-disabled"}): # this is the very last page, where the 'next' button is disabled
        url = "https://www.amazon.com" + str(pages.find("a", {"class": "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"})["href"])
            # if you go to any other page that isn't the last, what does the 'next' button give
            # make sure to look at the string
        return url
    else:
        return


while True:
    soup = getdata(url)
    getdeals(soup)
    url = getnextpage(soup)
    if not url:
        break
    else:
        print(url)
        print(len(dealslist))


df = pd.DataFrame(dealslist)
df["percentoff"] = 100 - ((df.saleprice / df.oldprice) * 100)
df = df.sort_values(by=["percentoff"], ascending=False)
print(df.head())
df.to_csv(searchterm + "-dailyamazondeals.csv", index=False)
print("Fin")

