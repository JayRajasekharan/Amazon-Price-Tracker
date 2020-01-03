import re
import smtplib

import requests
from bs4 import BeautifulSoup

from settings import from_server, from_port, from_user, from_password, to_email


def import_price_list():
    return None


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

    title = soup.find(id="productTitle").get_text()
    price = soup.find(id="priceblock_ourprice").get_text()

    # Price can contain currency symbols and "CAD"
    price = float(re.findall(r"\d+.\d+", price)[0])

    print(title.strip())
    print(price)

    # If Prices less that target price, send email
    if price < 10.00:
        send_email(title, price, URL)


def send_email(title, price, URL):
    subject = f"Price of {title} dropped!"
    body = f"Price dropped to {price}.\nCheck amazon link {URL}"

    message = "Subject: {}\n\n{}".format(subject, body)

    try:
        server = smtplib.SMTP(from_server, from_port)
        server.connect(from_server, from_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(from_user, from_password)
        server.sendmail(from_user, to_email, message)
        server.quit()
        print("Email sent successfully")
    except:
        print("Can't send email")


if __name__ == "__main__":
    check_price()
