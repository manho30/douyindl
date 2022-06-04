import asyncio
import json
from telebot.async_telebot import AsyncTeleBot
import requests
from helper import fing_url
import os

bot = AsyncTeleBot(
    '5556435695:AAEmgti4cF4IRi7BVb_d1v3ZXY6AlQyTpjU', parse_mode=None)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    await bot.reply_to(message, "Hello, I'm a bot that can help you download video from DouYin\n\n"
                       "Simply send me a link and I will download it for you.")


@bot.message_handler(commands=['help'])
async def send_help(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    await bot.reply_to(message, 'The operating principle of this bot is to request to the packaged API interface and then upload to Telegram\n\n'
                       'Source code: https://github.com/manho30/douyindlbot\n'
                       'API: https://github.com/manho30/douyinapi\n'
                       'Documentation: https://manho30.github.io/douyinapi/')


@bot.message_handler(regexp='http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
async def download(message):

    await bot.send_chat_action(message.chat.id, 'typing')
    wait = await bot.reply_to(message, '已将您的请求加入排队中...')

    res = fing_url.find_url(message.text)

    # check is res has more than one element
    if len(res) == 1:
        url = res[0]
        r = requests.get('https://douyinapi.herokuapp.com/api?url='+url)
        r = json.loads(r.text)
        try:
            if r['ok'] == True:

                # this is video
                uploading = await bot.edit_message_text(chat_id=message.chat.id,
                                                        message_id=wait.message_id,
                                                        text='{} 视频正在上传中...'.format(r['result']['video']['descriptions']))
                try:
                    await bot.send_chat_action(message.chat.id, 'upload_video')
                    await bot.send_video(message.chat.id,
                                        r['result']['video']['video_url']['free_watermark_1080p'],
                                        caption=r['result']['video']['descriptions'])
                    await bot.reply_to(message, '✅视频上传成功...')
                    await bot.delete_message(message.chat.id, uploading.message_id)
                except:
                    # 1080p is bigger than 50mb, try upload with 720p
                    reuploading = await bot.edit_message_text(chat_id=message.chat.id,
                                                            message_id=uploading.message_id,
                                                            text='⚠️视频大于50MB，正在重新上传...')
                    try:
                        # retry with 720p
                        await bot.send_chat_action(message.chat.id, 'upload_video')
                        await bot.send_video(message.chat.id,
                                            r['result']['video']['video_url']['free_watermark_720p'],
                                            caption=r['result']['video']['descriptions'])
                        await bot.reply_to(message, '✅视频上传成功...')
                        await bot.delete_message(message.chat.id, reuploading.message_id)
                    except:
                        # 720p is bigger than 50mb, upload failed
                        await bot.edit_message_text(chat_id=message.chat.id,
                                                    message_id=reuploading.message_id,
                                                    text='❌上传失败...')
            # api return error
            else:
                await bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=wait.message_id,
                                            text='❌上传失败...')
        except: 
            # this is picture
            await bot.send_chat_action(message.chat.id, 'upload_photo')
            uploading = await bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=wait.message_id,
                                        text='{} 图片正在上传中...'.format(r['result']['album']['descriptions']))
                                        
            await bot.send_chat_action(message.chat.id, 'upload_photo')
            
            try:
                for i in r['result']['album']['image_url']:
                    # download image to local
                    r = requests.get(i)
                    with open('image.jpg', 'wb') as f:
                        f.write(r.content)
                    # upload image to telegram
                    await bot.send_photo(message.chat.id, open('image.jpg', 'rb'))
                    os.remove('image.jpg')
                await bot.reply_to(message, '✅图片上传成功...')
                await bot.delete_message(message.chat.id, uploading.message_id)
            except:
                await bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=wait.message_id,
                                            text='❌上传失败...')

asyncio.run(bot.polling())
