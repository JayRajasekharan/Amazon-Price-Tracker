import json
import re
import smtplib
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

from settings import from_password, from_port, from_server, from_user, to_email


def import_price_list():
    with open("item_list.json", "r") as f:
        item_list = json.load(f)

    return item_list


def check_price():
    # URL to be tracked
    URL = "https://www.amazon.ca/Moneysworth-Best-Shoe-Cream-Black/dp/B00BVZ5ZR6/ref=sr_1_2?dchild=1&keywords=Moneysworth+and+Best+Shoe+Cream&qid=1578044020&s=sports&sr=1-2"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }

    page = requests.get(URL, headers=headers)

    # Amazon makes HTML code with javascript, so you can trick it using 2 soups
    soup = BeautifulSoup(page.content, "html.parser")
    soup = BeautifulSoup(soup.prettify(), "html.parser")

    title = soup.find(id="productTitle").get_text().strip()
    price = soup.find(id="priceblock_ourprice").get_text()

    # Price can contain currency symbols and "CAD"
    price = float(re.findall(r"\d+.\d+", price)[0])

    # If Prices less that target price, send email
    if price < 10.00:
        send_email(title, price, URL)


def send_email(title, price, URL):

    message = MIMEText(f"Price dropped to {price}. \nCheck amazon link: {URL}")
    message["Subject"] = f"Price dropped: {title}!"
    message["From"] = from_user
    message["To"] = to_email

    # print(message.as_string())

    try:
        server = smtplib.SMTP(from_server, from_port)
        server.connect(from_server, from_port)
        server.starttls()
        server.ehlo()
        server.login(from_user, from_password)
        server.sendmail(from_user, to_email, message.as_string())
        server.quit()
        print("Email sent successfully")
    except:
        print("Can't send email")


if __name__ == "__main__":
    check_price()
    # item_list = import_price_list()
    # print(item_list)
    # print(type(item_list))
    # print(item_list.keys())
