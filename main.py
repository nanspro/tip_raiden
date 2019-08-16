import tweepy
import logging
import time, requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

auth = tweepy.OAuthHandler("", "")
auth.set_access_token("", "")

api = tweepy.API(auth)
users = {}
users["@sounak98"] = "0x66b9BD3a9F0d44121533F88C94D4e35213222917"
tokens = ["0x380EB4e2C14ee155DBb55Ee1670B3B2f5b34eC85"]
# users["sounak98"] = "0x66b9BD3a9F0d44121533F88C94D4e35213222917"
BOT_OWNER = '@nanspr0'
TOKEN_ADDRESS = "0x380EB4e2C14ee155DBb55Ee1670B3B2f5b34eC85"
URL = 'http://localhost:5001/api/v1/'

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


def sync(api, since_id):
    logger.info("Retrieving Bot Mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.user_timeline, since_id = since_id).items():
        # print(tweet)
        # print(tweet.text.lower().split()[0])
        # and (tweet.user.screen_name == BOT_OWNER):
        if tweet.in_reply_to_status_id_str is None:
            if (tweet.text.lower().split()[0] == "@tip_raiden"):
                print(tweet.text.lower().split()[0])
                print(tweet.text)
                new_since_id = max(tweet.id, new_since_id)
            
                print(tweet.in_reply_to_status_id_str)
                #  Payment Method
                if any(keyword in tweet.text.lower() for keyword in ["add", "register"]):
                    logger.info(f"Bot Owner {tweet.user.name}")
                    logger.info(f"Answering to tweet {tweet.text}")

                    text = tweet.text.lower().split(" ")
                    text = text[1:]
                    text = filtering(text)
                    count = 0
                    for item in text:
                        if item == 'add' or item == 'register':
                            tokens.append(text[count + 1])
                            print(tokens)
                            break
                        count = count + 1
                    url = URL + 'tokens/' + str(tokens[len(tokens) - 1])
                    print(url)
                    x = requests.put(url)
                    print(x)
                    api.update_status(
                        status="You've added " + str(tokens[len(tokens) - 1]) + " as a mode of payment ",
                        in_reply_to_status_id=tweet.id,
                    )
                elif any(keyword in tweet.text.lower() for keyword in ["subscribe"]):
                    logger.info(f"Bot Owner {tweet.user.name}")
                    logger.info(f"Answering to tweet {tweet.text}")

                    text = tweet.text.split(" ")
                    text = text[1:]
                    count = 0
                    print("Hello")
                    print(text)
                    text = filtering(text)
                    for item in text:
                        if item == 'subscribe':
                            print(text)
                            partner = text[count + 1]
                            users[partner] = text[count + 2]
                            token = text[count + 3]
                            deposit = text[count + 4]                                                                                                                               
                            print("lalal")
                            if token not in tokens:
                                count = 0
                                print("lolol")
                                break
                            else:
                                break
                        count = count + 1
                    if count != 0:
                        print("hey")
                        print(users[partner], token, deposit)
                        if not api.get_user(partner).following:
                            api.get_user(partner).follow()
                        url = URL + 'channels'
                        print(url)
                        x = requests.put(url, headers={ 'Content-Type': 'application/json', }, json={ 'partner_address': users[partner], 'settle_timeout': 500, 'token_address': token, 'total_deposit': deposit, })
                        print(x)
                        api.update_status(
                            status="You've been subscribed to " + partner + " on " + token + " with deposit of " + deposit + " tokens" ,
                            in_reply_to_status_id=tweet.id,
                        )
                    else:
                        api.update_status(
                            status="Please register for the given token address first",
                            in_reply_to_status_id=tweet.id,
                        )
        else:
            if (tweet.text.lower().split()[1] == "@tip_raiden"):
                print(tweet.text.lower().split()[1])
                print(tweet.text)
                new_since_id = max(tweet.id, new_since_id)
            
                print(tweet.in_reply_to_status_id_str)
                print("start")
                partner = tweet.text.lower().split()[0]
                if partner not in users.keys():
                    api.update_status(
                        status="Please subscribe to the user first",
                        in_reply_to_status_id=tweet.id,
                    )
                    break
                addr = users[partner]
                
                print(addr)

                logger.info(f"Paying to {partner}")
                # logger.info(f"Paying for tweet {prev_tweet.text}")

                text = tweet.text.split(" ")
                text = filtering(text)
                amount = text[2]
                token_addr = text[3]
                print("pop")
                print(text[2], text[3])
                url = URL + 'payments/' + token_addr + '/' + addr
                print(url)
                x = requests.post(url, headers={ 'Content-Type': 'application/json', }, json={ 'amount': amount, 'identifier': 1, })
                print(x)
                api.update_status(
                    status="Successfully sent tip worth " + amount,
                    in_reply_to_status_id=tweet.id,
                )
    return since_id

def filtering(text):
    length = len(text)
    n = ''
    i = 0
    while(i<length):
        if(text[i]==n):
            text.remove(text[i])
            length = length -1  
            continue
        i = i+1
    i = 0
    n = '\n'
    length = len(text)
    while(i<length):
        if(text[i]==n):
            text.remove(text[i])
            length = length -1  
            continue
        i = i+1
    return text

def main():
    since_id = 1
    while True:
        print(since_id)
        since_id = sync(api, since_id)
        print("pil")
        print(since_id)
        logger.info("Waiting...")
        time.sleep(10)

if __name__ == "__main__":
    main()