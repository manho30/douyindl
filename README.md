# DouYin Downloader Bot
DouYin Downloader Bot provide a service allow you
download stream video in Telegram Platform.

## How to use
1. Add DouYin Downloader Bot to your group.
2. Send a DouYin video link to the bot.
3. The bot will reply a video file.

## Local Deploy
1. Clone this repository.
```bash
$ git clone https://github.com/manho30/douyindl.git
$ cd douyindl
```

2. Install all dependencies.
```bash
$ pip install -r requirements.txt
```

3. Change the config in `config.py`.
```python
TOKEN = 'YOUR_BOT_TOKEN'
```

4. Run the bot.
```bash
$ python bot.py
```

## Deploy to Heroku
You may also deploy to Heroku as you like.

Check out this [Video](https://youtu.be/_WxRbxK2CIA) for more information.