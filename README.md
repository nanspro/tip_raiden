# Micropayments on Twitter
Ever came across interesting content on twitter and want to appreciate the creator ? How about getting a subscription for articles, videos, funny tweets or any digital content ? 
The above issues can be solved by introducing micropayments on the world's most popular microblogging service. Imagine just by replying to a tweet you liked, you can tip the person directly in seconds. Taking a subscription of something and paying regularly as they deliver their content to you instead of just upfront paying all the money.

Now all these things are possible, thanks to raiden network's offchain payments and this twitter bot.

## How to get started
1. Just go to https://developer.twitter.com/en/apps and create your own tipping bot. This is because you can only interact with twitter APIs through an app.
2. After creating an app, just go to details and note down API keys and Access Tokens (along with secret).
3. Clone this repository using `git clone https://github.com/nanspro/tip_raiden`
    ```python
    cd tip_raiden
    pip3 install -r requirements.txt
    ```
4. Copy your app keys and tokens into .env file
5. Run a raiden node locally. For more info, visit https://raiden-network.readthedocs.io/en/latest/overview_and_guide.html#firing-it-up
6. Copy your RPC url for running node into .env too
7. `python3 main.py`

Running this script/bot will listen to your tweets and respond accordingly. Let's see what all can you do after all this!!

## Stuff that you can do while sitting on your couch scrolling twitter through your mobile phone

### Subscribing for some community or individual
```
@tip_raiden blahblahblah... subscribe @user <User_Ethereum_Address> <Token_Addr> <Deposit> blahblahblah...
```

This will add @user to your list of subscriptions with his ethereum address. @user and his address must be written together separated by a single space.
Your bot will create a channel to that ethereum address with your current set token_address and will reply back to your tweet with the response.

### Adding a new payment method
Suppose you want to tip someone using another kind of token. Just register that token to your node by
```
@tip_raiden ... add/register <Token_Addr> ...
```
Token_Addr should follow "add" or "register" after space.

### Paying to the user/service provider
You can tip anyone for their particular tweet by replying to that tweet with a particular message
```
@tip_raiden <amount> <token_addr>
```
amount is an integer and should be less than your total token ammount. You must have a channel where your partner is this user with your current token_address. Bot will send the amount to the user in the background and on success will let you know by replying back on your tweet with the response.