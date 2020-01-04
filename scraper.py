import json
import re
import smtplib
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

# setting.py contains the server, port, and email info for the sending and receiving emails
from settings import from_password, from_port, from_server, from_user, to_email


def import_price_list():
    """
    Reads the items_list.json file and imports a list of items to price check
    """
    with open("item_list.json", "r") as f:
        item_list = json.load(f)

    return item_list


def save_price_list(item_list):
    """
    Saves the item_list to json file
    """
    with open("item_list.json", "w") as fout:
        json.dump(item_list, fout)


def check_price(URL, headers):
    """
    Scrapes Amazon.ca and obtiains the price of the item. If the prices is below a target prices
    (obtained from items_list.json), then it will send and email with price alert.
    Returns: price of the item
    """
    page = requests.get(URL, headers=headers)

    # Amazon makes HTML code with javascript, so you can trick it using 2 soups
    soup = BeautifulSoup(page.content, "html.parser")
    soup = BeautifulSoup(soup.prettify(), "html.parser")

    title = soup.find(id="productTitle").get_text().strip()
    price = soup.find(id="priceblock_ourprice").get_text()

    # Price can contain currency symbols and "CAD"
    price = float(re.findall(r"\d+.\d+", price)[0])

    return (
        price,
        title,
    )


def send_email(title, price, URL):
    """
    Helper function to send email with the price alert details.
    Requires the server, port, user email and password for the sending email.
    """
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
    except Exception as e:
        print("Can't send email")
        print(e)


if __name__ == "__main__":

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }

    # Import list of items to check
    item_list = import_price_list()

    for index, item in enumerate(item_list):

        item_name = item["item_name"]
        item_url = item["item_url"]
        target_price = item["target_price"]
        last_price = item["last_price"]

        # Check latest price from Amazon
        print(f"Checking {item_name}")
        item_price, item_title = check_price(item_url, headers)
        print(f"{item_title}, {item_price}")

        # If current price is less that target price: send email
        if item_price < target_price:
            send_email(item_title, item_price, item_url)

        # If the item has dropped in the price since the last check, update "last_price"
        if item_price < last_price:
            item_list[index]["last_price"] = item_price

        # Update the changes to JSON file
        save_price_list(item_list)

    print(item_list)
