"""
Code for twitter tipping bot
"""

import logging
import time
import os
import requests
import tweepy
from dotenv import load_dotenv

load_dotenv(verbose=True)

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BOT_OWNER = os.getenv("ADMIN_USERNAME")
URL = os.getenv("URL")

AUTH = tweepy.OAuthHandler(API_KEY, API_SECRET)
AUTH.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

API = tweepy.API(AUTH)
USERS = {}
# USERS["@sounak98"] = "0x679D63F719f4F179c0AFfc16DEA71e1C2C843e33"
TOKENS = ["0x380EB4e2C14ee155DBb55Ee1670B3B2f5b34eC85"]
# USERS["sounak98"] = "0x66b9BD3a9F0d44121533F88C94D4e35213222917"
TOKEN_ADDRESS = "0x380EB4e2C14ee155DBb55Ee1670B3B2f5b34eC85"
# URL = 'http://localhost:5001/api/v1/'

try:
    API.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


def filtering(text):
    """ Filter empty spaces and new lines from text """
    length = len(text)
    n_0 = ''
    i = 0
    while i < length:
        if text[i] == n_0:
            text.remove(text[i])
            length = length - 1
            continue
        i = i + 1
    i = 0
    n_0 = '\n'
    length = len(text)
    while i < length:
        if text[i] == n_0:
            text.remove(text[i])
            length = length - 1
            continue
        i = i + 1
    return text


def register_token(tweet):
    """ Adding a new token as a mode of payment """
    LOGGER.info(f"Bot Owner {tweet.user.name}")
    # LOGGER.info(f"Answering to tweet {tweet.text}")

    text = tweet.text.lower().split(" ")
    text = text[1:]
    text = filtering(text)
    count = 0
    for item in text:
        if item in ("add", "register"):
            token = text[count + 1]
            break
        count = count + 1
    return token


def subscribe(tweet):
    """ Subscribing to a new user """
    LOGGER.info(f"Bot Owner {tweet.user.name}")
    # LOGGER.info(f"Answering to tweet {tweet.text}")

    text = tweet.text.split(" ")
    text = text[1:]
    count = 0
    # print(text)
    text = filtering(text)
    for item in text:
        if item == 'subscribe':
            print(text)
            partner = text[count + 1]
            partner_addr = text[count + 2]
            token_addr = text[count + 3]
            amount = text[count + 4]
            if token_addr not in TOKENS:
                count = 0
                break
            else:
                count = 1
                break
        count = count + 1
    return partner, partner_addr, token_addr, amount, count


def add_money(tweet):
    """ Depositing more tokens in a channel with user """
    LOGGER.info(f"Bot Owner {tweet.user.name}")
    # LOGGER.info(f"Answering to tweet {tweet.text}")

    text = tweet.text.split(" ")
    text = text[1:]
    text = filtering(text)
    count = 0
    for item in text:
        # print(item)
        if item in USERS.keys():
            amount = text[count + 1]
            partner = USERS[item]
            token_addr = text[count + 2]
            break
        count = count + 1
    return amount, partner, token_addr


def pay(tweet, since_id):
    """ Pay to user which you have subscribed to """
    # Extracting info from tweet which is meant to pay

    # print(tweet.text.lower().split()[1])
    # print(tweet.text)
    new_since_id = max(tweet.id, since_id)

    # print(tweet.in_reply_to_status_id_str)
    partner = tweet.text.lower().split()[0]
    text = tweet.text.split(" ")
    text = filtering(text)
    amount = text[2]
    token = text[3]
    if partner not in USERS.keys():
        partner = ""
    return partner, token, amount, new_since_id


def unsubscribe(tweet):
    """ Unsubscribe from a user and close the channel with him """
    LOGGER.info(f"Bot Owner {tweet.user.name}")
    LOGGER.info(f"Answering to tweet {tweet.text}")

    text = tweet.text.split(" ")
    text = text[1:]
    text = filtering(text)
    count = 0
    for item in text:
        print(item)
        if item in USERS.keys():
            partner = USERS[item]
            token_addr = text[count + 1]
            break
        count = count + 1
    return partner, token_addr


def sync(api, since_id):
    """ Listening for bot mentions and responding accordingly to
        the tweet content """
    LOGGER.info("Retrieving Bot Mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.user_timeline, since_id=since_id).items():
        # Not a reply to any tweet
        if tweet.in_reply_to_status_id_str is None:
            if tweet.text.lower().split()[0] == "@tip_raiden":

                # print(tweet.text.lower().split()[0])
                # print(tweet.text)
                new_since_id = max(tweet.id, new_since_id)
                # print(tweet.in_reply_to_status_id_str)
                # Registering a new token
                if any(keyword in tweet.text.lower()
                       for keyword in ["add", "register"]):
                    token = register_token(tweet)
                    TOKENS.append(token)
                    url = URL + 'tokens/' + str(TOKENS[len(TOKENS) - 1])
                    # print(url)
                    resp = requests.put(url)
                    print(resp)
                    API.update_status(
                        status="You've added " + str(TOKENS[len(
                            TOKENS) - 1]) + " as a mode of payment ",
                        in_reply_to_status_id=tweet.id,
                    )

                # Subscribing to a user
                elif any(keyword in tweet.text.lower()
                         for keyword in ["subscribe"]):
                    partner, addr, token, deposit, count = subscribe(tweet)
                    USERS[partner] = addr
                    if count != 0:
                        # print("hey")
                        print(USERS[partner], token, deposit)
                        if not API.get_user(partner).following:
                            API.get_user(partner).follow()
                        url = URL + 'channels'
                        resp = requests.put(url, headers={'Content-Type': 'application/json', }, json={'partner_address': USERS[partner], 'settle_timeout': 500, 'token_address': token, 'total_deposit': deposit, })
                        if resp.status_code == 201:
                            API.update_status(
                                status="You've been subscribed to " + partner + " on " + token + " with deposit of " + deposit + " tokens",
                                in_reply_to_status_id=tweet.id,
                            )
                        else:
                            print(resp.status_code)
                    else:
                        API.update_status(
                            status="Please register for the given token address first",
                            in_reply_to_status_id=tweet.id,
                        )

                #  Increase collateral on a subscription
                elif any(keyword in tweet.text.lower() for keyword in ["increase"]):
                    amount, partner, token_addr = add_money(tweet)
                    url = URL + 'channels/' + token_addr + '/' + partner
                    resp = requests.patch(url, headers={'Content-Type': 'application/json', }, json={'total_deposit': amount, })
                    print(resp)
                    API.update_status(
                        status="You've deposited " + str(amount) + " tokens for the channel",
                        in_reply_to_status_id=tweet.id,
                    )
                # Only available in version 0.100.4

                elif any(keyword in tweet.text.lower() for keyword in ["decrease", "withdraw"]):
                    LOGGER.info(f"Bot Owner {tweet.user.name}")
                    LOGGER.info(f"Answering to tweet {tweet.text}")

                    text = tweet.text.split(" ")
                    text = text[1:]
                    text = filtering(text)
                    print(text)
                    count = 0
                    for item in text:
                        print(item)
                        if item in USERS.keys():
                            amount = text[count + 1]
                            partner = USERS[item]
                            token_addr = text[count + 2]
                            break
                        count = count + 1
                    url = URL + 'channels/' + token_addr + '/' + partner
                    print(url)
                    resp = requests.patch(url, headers={'Content-Type': 'application/json', }, json={'total_withdraw': amount, })
                    print(resp)
                    API.update_status(
                        status="You've withdrawn " + str(amount) + " tokens from the channel",
                        in_reply_to_status_id=tweet.id,
                    )

                # Unsubscribe from a user
                elif any(keyword in tweet.text.lower() for keyword in ["close", "unsubscribe"]):
                    partner, token_addr = unsubscribe(tweet)
                    url = URL + 'channels/' + token_addr + '/' + partner
                    print(url)
                    resp = requests.patch(url, headers={'Content-Type': 'application/json', }, json={'state': 'closed', })
                    print(resp)
                    API.update_status(
                        status="You've closed the connection with this channel",
                        in_reply_to_status_id=tweet.id,
                    )
        else:
            # Replying to someone else's tweet.
            if tweet.text.lower().split()[1] == "@tip_raiden":
                partner, token, amount, new_since_id = pay(tweet, new_since_id)
                if partner == "":
                    API.update_status(
                        status="Please subscribe to the user first",
                        in_reply_to_status_id=tweet.id,
                    )
                    return since_id
                addr = USERS[partner]

                LOGGER.info(f"Paying to {partner}")
                # LOGGER.info(f"Paying for tweet {prev_tweet.text}")

                url = URL + 'payments/' + token + '/' + addr
                print(url)
                resp = requests.post(url, headers={'Content-Type': 'application/json', }, json={'amount': amount, 'identifier': 1, })
                print(resp)
                API.update_status(
                    status="Successfully sent tip worth " + amount,
                    in_reply_to_status_id=tweet.id,
                )
    return since_id


def main():
    """ Infinite loop which runs forever """
    since_id = 1
    while True:
        print(since_id)
        since_id = sync(API, since_id)
        LOGGER.info("Waiting...")
        time.sleep(10)


if __name__ == "__main__":
    main()
