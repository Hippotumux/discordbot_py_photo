import discord
import json
import time
import os
import requests
from pprint import pprint
from bs4 import BeautifulSoup


client = discord.Client()

# https://www.pixiv.net/ajax/search/artworks/%E4%BC%81%E9%B5%9D?word=%E4%BC%81%E9%B5%9D&order=date_d&mode=all&p=1&s_mode=s_tag&type=all&lang=zh_tw

f = open('token.json')
data = json.load(f)

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'cookie' : data['cookie'],
    'Referer' : 'https://www.pixiv.net/'
}

params = {
    'word'   : '企鵝',
    'order'  : 'date_d',
    'mode'   : 'all',
    'p'      : '1',
    's_mode' : 's_tag_full',
    'type'   : 'manga',
    'lang'   : 'zh_tw'
}


    
@client.event
async def on_ready():
    print('目前登入身分' , client.user)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'ping':
        await message.channel.send('pong')
        return 
    if message.content.startswith('$'):
        tmp = message.content.split(" ",1)        
    # if len(tmp) <= 2 or int(tmp[2])<=0 or int(tmp[2])>5:
      #       await message.channel.send("輸入錯誤 或數量>5")
      #      return 

      #  params['word'] = tmp[1]

        #response = requests.get('https://www.pixiv.net/ajax/search/artworks/' + params['word'] + '?',params = params,headers = headers).text
        response = requests.get('https://www.pixiv.net/ajax/user/'+tmp[1]+'/profile/all',headers = headers)
        if response.status_code == 404:
            await message.channel.send('找不到網頁')
            return
        response = response.text
        res = json.loads(response)
        body = res['body']['illusts']
        await message.channel.send('總共的圖片數量:'+str(len(body))+" 但只會輸出10張求我啊呵")
        x=0
        for key in body:
            print("ok")
            if x > 10 :
                return
            x+=1
            print(key)
            tx = requests.get('https://www.pixiv.net/ajax/illust/'+key,headers = headers,timeout=3)
            if tx.status_code != 200:
                print("error")
                x-=1
                continue
            print(tx.status_code)
            tx=tx.text
            r = json.loads(tx)
            b = r['body']['urls']['original']
            if not os.path.exists("images"):
                os.mkdir("images")
            img = requests.get(b,headers = headers)
            if img.status_code != 200:
                print("wrong")
                x-=1
                continue
            if os.path.exists("images/1.jpg"):
                os.remove("images/1.jpg")
            with open("images/" + "1" + ".jpg", "wb") as file:
                file.write(img.content)
            pic = discord.File("images//1.jpg")
            byte_size = os.path.getsize("images//1.jpg")
            mb_size = int(byte_size/(1024*1024))
            if mb_size>7:
                print("檔案過大跳過")
                x-=1
                continue
            await message.channel.send(file=pic)
            os.remove("images/1.jpg")
            time.sleep(2)
client.run(data['token'])
