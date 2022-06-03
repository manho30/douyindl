import json
import telepot
import requests
from telepot.loop import MessageLoop
from helper import fing_url
import re
import os

bot = telepot.Bot('5556435695:AAEmgti4cF4IRi7BVb_d1v3ZXY6AlQyTpjU')

def handleText(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        text = msg['text']
        
        if text == '/start':
            bot.sendChatAction(chat_id, 'typing')
            bot.sendMessage(chat_id, 'Hello, I am a bot! You can jus send me a link consits of DouYin video and I will download it for you!') 
            
        else:
            if text == '/help':
                bot.sendChatAction(chat_id, 'typing')
                bot.sendMessage(chat_id, 'The operating principle of this bot is to request to the packaged API interface and then upload to Telegram\n\n'
                                        'Source code: https://github.com/manho30/douyindlbot\n'
                                        'API: https://github.com/manho30/douyinapi\n'
                                        'Documentation: https://manho30.github.io/douyinapi/')
            else:
                
                bot.sendChatAction(chat_id, 'typing')
                wait = bot.sendMessage(chat_id, '已将您的请求加入排队中...')
                res = fing_url.find_url(text)
                
                # check is res has more than one element
                if len(res) == 1:
                    url = res[0]
                    r = requests.get('https://douyinapi.herokuapp.com/api?url='+url)
                    r = json.loads(r.text)
                    try:
                        bot.sendChatAction(chat_id, 'typing')
                        sending = bot.editMessageText(telepot.message_identifier(wait), '图文: 《{}》 正在发送中...'.format(r['result']['album']['descriptions']))
                        for i in r['result']['album']['image_url']:
                            bot.sendChatAction(chat_id, 'upload_photo')
                            # download image to local and convert it from webp to jpg
                            r = requests.get(i)
                            with open('image.jpg', 'wb') as f:
                                f.write(r.content)
                            # send image
                            bot.sendPhoto(chat_id, open('image.jpg', 'rb'))
                        
                            os.remove('image.jpg')
                        bot.deleteMessage(telepot.message_identifier(sending))
                        bot.sendMessage(chat_id, '发送成功✅')
                    
                    except:
                        try:
                            bot.sendChatAction(chat_id, 'typing')
                            sending = bot.editMessageText(telepot.message_identifier(wait), '视频: 《{}》 正在发送中...'.format(r['result']['video']['descriptions']))
                            bot.sendChatAction(chat_id, 'upload_video')
                            bot.sendVideo(chat_id, r['result']['video']['video_url']['free_watermark_1080p'], caption=r['result']['video']['descriptions'])
                            bot.deleteMessage(telepot.message_identifier(sending))
                            bot.sendMessage(chat_id, '发送成功✅')
                        except:
                            bot.sendChatAction(chat_id, 'typing')
                            try:
                                again = bot.editMessageText(telepot.message_identifier(wait), '视频过大，正在重新上传⚠️')
                                bot.sendChatAction(chat_id, 'upload_video')
                                bot.sendVideo(chat_id, r['result']['video']['video_url']['free_watermark'], caption=r['result']['video']['descriptions'])
                                bot.deleteMessage(telepot.message_identifier(again))
                                bot.sendMessage(chat_id, '发送成功✅')
                            except:
                                bot.sendChatAction(chat_id, 'typing')
                                bot.editMessageText(telepot.message_identifier(wait), '视频过大，无法上传❌')
                    
                else:
                    bot.editMessageText(telepot.message_identifier(wait), 'No url found')

MessageLoop(bot, {
    'chat': handleText,
}).run_forever()