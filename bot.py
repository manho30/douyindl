import json
import telebot 
from telebot import types
import requests
import os

from helper import find_url
from api import scraper

# init the scraper
douyinClient = scraper.Douyin()

bot = telebot.TeleBot('5556435695:AAEmgti4cF4IRi7BVb_d1v3ZXY6AlQyTpjU', parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, "Hello, I'm a bot that can help you download video from DouYin\n\n"
                          "Simply send me a link and I will download it for you.")


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, 'The operating principle of this bot is to request to the packaged API interface and then upload to Telegram\n\n'
                          'Source code: https://github.com/manho30/douyindlbot\n'
                          'API: https://github.com/manho30/douyinapi\n'
                          'Documentation: https://manho30.github.io/douyinapi/')

@bot.inline_handler(lambda query: query)
def querytext(inline_query):
    r = types.InlineQueryResultArticle('1', title=f"Tap to send '{inline_query.query}' as spoiler", 
                                            description=f'||{inline_query.query}||', 
                                            input_message_content=types.InputTextMessageContent(f'<tg-spoiler>{inline_query.query}</tg-spoiler>', parse_mode = 'HTML'))
    bot.answer_inline_query(inline_query.id, [r])
    
@bot.message_handler(regexp='http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
def download(message):

    bot.send_chat_action(message.chat.id, 'typing')
    wait = bot.reply_to(message, '已将您的请求加入排队中...')

    res = find_url.find_url(message.text)

    # check is res has more than one element
    if len(res) == 1:
        url = res[0]
        r = douyinClient.douyin(url=url)
        #r = json.loads(r.text)
        try:
            if r['ok'] == True:

                # this is video
                uploading = bot.edit_message_text(chat_id=message.chat.id,
                                                        message_id=wait.message_id,
                                                        text='{} 视频正在上传中...'.format(r['result']['video']['descriptions']))
                try:
                    bot.send_chat_action(message.chat.id, 'upload_video')
                    bot.send_video(message.chat.id,
                                        r['result']['video']['video_url']['free_watermark_1080p'],
                                        caption='{} - {}'.format(r['result']['author']['name'], r['result']['video']['descriptions']))
                    bot.reply_to(message, '✅视频上传成功...')
                    bot.delete_message(message.chat.id, uploading.message_id)
                except:
                    # 1080p is bigger than 50mb, try upload with 720p
                    reuploading = bot.edit_message_text(chat_id=message.chat.id,
                                                            message_id=uploading.message_id,
                                                            text='⚠️视频大于50MB，正在尝试重新上传...')
                    try:
                        # retry with 720p
                        bot.send_chat_action(message.chat.id, 'upload_video')
                        bot.send_video(message.chat.id,
                                            r['result']['video']['video_url']['free_watermark'],
                                            caption='{} - {}'.format(r['result']['author']['name'], r['result']['video']['descriptions']))
                        bot.reply_to(message, '✅视频上传成功...')
                        bot.delete_message(message.chat.id, reuploading.message_id)
                    except:
                        # 720p is bigger than 50mb, upload failed, send a shorten link to user
                        shorten = requests.get('https://cutt.ly/api/api.php?key={}&short={}'.format('cfce60a1a0e5aeb95dac99ebdc3cc6299ede9', r['result']['video']['video_url']['free_watermark_1080p']))
                        shorten = json.loads(shorten.text)
                        try:
                            bot.edit_message_text('因视频庞大无法上传， 请点击以下链接自行下载：\n{}'.format(shorten['url']['shortLink']).replace('/\'', ''),
                                                  message.chat.id, reuploading.message_id,)
                        except:
                            bot.edit_message_text(chat_id=message.chat.id,
                                                  message_id=reuploading.message_id,
                                                  text='❌上传失败...')
            # api return error
            else:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=wait.message_id,
                                      text='❌上传失败...')
        except: 
            # this is picture
            bot.send_chat_action(message.chat.id, 'upload_photo')
            uploading = bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=wait.message_id,
                                        text='{} 图片正在上传中...'.format(r['result']['album']['descriptions']))
                                        
            bot.send_chat_action(message.chat.id, 'upload_photo')
            
            try:
                for i in r['result']['album']['image_url']:
                    # download image to local
                    r = requests.get(i)
                    with open('image.jpg', 'wb') as f:
                        f.write(r.content)
                    # upload image to telegram
                    bot.send_photo(message.chat.id, open('image.jpg', 'rb'))
                    os.remove('image.jpg')
                bot.reply_to(message, '✅图片上传成功...')
                bot.delete_message(message.chat.id, uploading.message_id)
            except:
                bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=wait.message_id,
                                            text='❌上传失败...')
                                            
bot.polling()