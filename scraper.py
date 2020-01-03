import requests
from bs4 import BeautifulSoup

URL = "https://www.amazon.ca/Moneysworth-Best-Shoe-Cream-Black/dp/B00BVZ5ZR6/ref=sr_1_2?dchild=1&keywords=Moneysworth+and+Best+Shoe+Cream&qid=1578044020&s=sports&sr=1-2"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}

page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")

print(soup.prettify())
