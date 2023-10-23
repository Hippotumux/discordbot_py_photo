# DC機器人爬蟲(python)

> 此專案目的為做一個 DC 機器人，並且到 pixiv 抓取圖片並且傳到 DC 群組

之前做過用 js 去抓不需要登入的網站，然後找簡單暴力搜 html 的 url 而已。
而不知道為什麼放進 docker 就壞掉了，弄了超久才發現是版本沒到最新，還有一些 nvm 的問題，所以後來我就放棄用 js 改成用 python 寫。

## 功能

讓使用者輸入繪師 id ，回傳前 10 張圖片到 DC 上。
如果爬不到的話會輸出找不到網頁。

## 畫面

![image](https://github.com/Hippotumux/discordbot_py_photo/assets/100692893/1fe52a42-d57e-43fe-9aa0-462630869cfb)

## 安裝

需要安裝 docker / docker compose 

```
sudo apt-get -y docker-compose
sudo apt-get install docker.io
```


### 取得專案

```bash
git clone git@github.com:Hippotumux/discordbot_py_photo.git
```

### 前言
pixiv 需要登入才能請求到比較完整的資料，但是寫登入稍微麻煩了點，所以我實作直接丟 cookie 去抓資料(但要注意 cookie 經過一段時間之後，會變動) 
- 這次的實作是給繪師 id，然後爬蟲下載到本地端並且傳送到 discord 上面
- 並且使用 docker compose 來跑

## 請求

### coockie
瀏覽網站時，設定於瀏覽器內的 Cookies，會讓瀏覽器記下一些特定的資訊以便未來能夠更加方便被使用。也就是說如果用登入過後的 cookie 去訪問 pixiv 他就會根據你的登入過的 cookie 給你登入後應該得到的訊息

尋找 pixiv 的 cookie:
- 先到 pixiv 登入之後，到網頁按 f12 到 network 重刷頁面會出現他跑過的東西，找到 pixiv.net 裡面的 cookie 就是你的 cookie
![](https://i.imgur.com/OC7PHsM.png)


### User-Agent
user-Agent 指的是代表使用者行為的程式，垃圾郵件機器人和網路爬蟲經常使用假的使用者代理。我們是乖寶寶所以我們要放自己的 user-Agent，如何找到 User-Agent
- 在剛剛找 cookie 的地方，下面會有 request header，裡面放的 User-Agent: 就是你本機。![](https://i.imgur.com/e0pkgkH.png)


### referer問題
referer 是 HTTP 的參照位址，藉著 HTTP 參照位址，目前的網頁可以檢查訪客從哪裡而來，這也常被用來對付偽造的跨網站請求。

<strong><font color = "red">在pixiv會遇到的問題</strong></font>:
- 如果直接在分頁上面輸入 Pixiv 其中一張作品的圖片連結，所以 referer 的欄位不會被填入任何東西。Pixiv 的圖片伺服器不知道你從哪裡來的，但他們可以藉此推測反正你一定不是從他們網站上面讀取，所以它可以選擇不把圖片回傳給你，一樣死圖：
![](https://i.imgur.com/LbrpMZA.png)

這是什麼意思呢？假設你現在正在瀏覽一個網頁：
https: // 127.0.0.1/index.php
我們要去瀏覽其他網頁圖片的時候這時候，你的瀏覽器為了要讀取這張圖片，因此傳送請求給 192.168.0.1 這個伺服器。當瀏覽器傳送連線請求給它們的時候，就會透過 referer 欄位的資訊順帶告訴伺服器：「嗨！我要讀取你伺服器上面的 /imgs.jpg，還有，我是從 https ://127.0.0.1/ 這個網站間接連過來的。」

而且因為 pixiv 遇到不是從他們網站上面讀取的就會拒絕
所以我們可以仿冒:把自己的 referer 欄位填入https://pixiv.net/ 來讓 Pixiv 的圖片伺服器以為我們是從 Pixiv .net 上面讀取這張圖片：

![](https://i.imgur.com/4CQw4Ql.png)

### 請求:
剛剛提到的 cookie referer user-Agent 就是 Request header 的一部分，可以再請求 pixiv 的時候讓他知道你的一些資料。

常見三種請求方式:
- GET : 目的是請求展示指定資源。使用 GET 的請求只應用於取得資料。
- HEAD : 很像 GET，不過 server 不能回傳給你 body (信息主體)
- POST : 傳遞資料時會將資料放進 message body 進行傳送

因為我們是要爬蟲抓取圖片網址所以我們用 request get 去抓取網站資訊，再去抓取裡面的 url。

## python爬蟲實作
### 如何得到網頁資訊
    
- 利用 python 的 request get 取得資料 (response)，headers 就是上面提到的 cookie user-Agent referer. 因為我們要的是網站內容，所以取得他的 text
![](https://i.imgur.com/G1UPLXO.png)


- 利用 python request 得到的東西轉成 json 檔案，方便解析，也可以用暴力搜，找到關鍵字，不過 json 還是方便很多。
![](https://i.imgur.com/SlSVMyu.png)

### 分析json檔案

<簡單從一個例子來看>
![](https://i.imgur.com/C7UBY8i.png)

我們可以看到在 Influencers 裡面放著兩個東西，這兩個東西個別有他們的 name , age , work at，
假設我們請求轉 json 得到的 res 存放的東西是上面那張圖的內容，就可以用 res['Influencers'] 得到兩個的資料，可以在個別解析 res['Influencers'][0] 就是第一個人的資料，想要看到他的名字就在繼續往下 res['Influencers'][0]['name'] 就可以得到 Jaxon

(小注意 如果我們在找尋的過程出現 [] 裡面必須放 integer 代表我們的這層資料是有多筆資料像是上面的 [0])

<font color = "red">注意 : 每個實作的東西都是要靠自己去慢慢尋找想要的部分，如果按照網路上直接跟你說他在哪個位置去寫程式是失去意義的。更何況不同地方得到的東西自然就不一樣。</font>

### 下載圖片

順利抓到資料後應該會得到像這樣的網址
![](https://i.imgur.com/UnbUis2.png)

我們就可以再透過 request get 這些網址來取得檔案內容，然後再透過 python 的 file.write 寫進去我們的檔案就好了。因為我們要寫入的是二進制，所以使用 wb 寫入 (一般寫入用 w 就好)
![](https://i.imgur.com/yPQhjNX.png)

可以注意到這邊我用的是 content 和 text 是不同的
- resp.text 返回的是 Unicode 型的。
resp.content 返回的是 bytes 型也就是二進位
文本用 text，、文件用 contexnt

### requirements

![](https://i.imgur.com/9FxEM1e.png)
以下操作安裝 (注意自己有沒有裝 pip 還有 discord.py 要 1.7.3 版本，過舊的版本格式什麼的都不一樣，網路上教學很多都不同版本的，常常會發現怎麼他能用自己實作卻不能用)
![](https://i.imgur.com/aTFMbM2.png)

簡單介紹一下上面的東西
- discord 就是用來用在 discord，像是機器人連線，機器人發訊息(發圖片)
- json 上面提到過，用來分析我們得到的資料。
- time 因為抓圖片抓太快可能會被認為是機器人，timesleep停個幾秒
- os 是一些系統的操作，可以建立資料夾，刪除檔案之類的。
- requests 就是用來請求
- pprint 他是一種數據美化輸出，這樣輸出得到的資料會比較好分析，如果單純用 print 會全部一坨

## DC 機器人建立，以及取得 token

因為步驟都一樣，所以這邊放上我參考的資料
https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token
就可以取得 token 了

## 更改 token.json

把得到的 cookie 以及 token 放進去 token.json

## 運行專案

```bash
docker compose up -d
```


## 說明

- volumn - 要放去 up 上去的資料夾
  - images - 取下來的圖片放置處
  - dcbot.py - 主要執行爬蟲跟和 DC 聊天室互動的程式
  - token.json - 存放 dc token 跟 cookie (記得放自己的，我已經把我自己的拿掉了)
...


## 聯絡作者

我是河馬 ~~ 很高興認識大家，如果有任何疑問請使用以下方式來聯絡我

- [Blog](https://hackmd.io/@HIPP0/notebook)
- [Facebook](https://www.facebook.com/profile.php?id=100008989923059)
- [Discord] 河馬#9738
...
