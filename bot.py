# -*- coding: utf-8 -*-

import logging, random
import requests
import os
import re
import json

import config

from flask import Flask, request,Response

app = Flask(__name__)
app.config.from_object(__name__)
app.logger.setLevel(logging.DEBUG)

LINE_ENDPOINT  = config.LINE_ENDPOINT
USER_LOCAL = config.USER_LOCAL
MICROSOFT = config.MICROSOFT
HEADERS = config.HEADERS

# 固定で返すメッセージ群
TALKS = [
        "hogehoge",
        "fugafuga",
        "ぬおおお",
        ]

@app.route("/")
def hello():
    return "umaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

@app.route("/callback", methods=["POST"])
def callback():
    # TODO Signature validation

    app.logger.info(request.json)
    app.logger.info(request.headers)
    req = request.json["result"][0]

    if req["eventType"] == "138311609100106403":
        """
        友だち申請の受信はここに来る。
        申請されたらすぐお礼メッセージを送る。
        TODO 未検証
        """

        send_text([req["content"]["from"]], u"Yo")

    elif req["eventType"] == "138311609000106303":
        """
        会話メッセージを受信した場合
        それ以外は準備したテキストをランダムで返す。
        """

        to = [req["content"]["from"]]
        message = req["content"]["text"]

    # if re.compile('の画像$').search(message) :
    #     message = re.split('の画像', message)
    #     images = search_image(message)
    #     # 写真送付
    #     i = random.randint(0, len(images) - 1)
    #     send_picture(to, images[i])
    # else :    
    send_message = get_send_message(message)
    send_text(to, send_message)


        # if message == u"若井友希":
        #     images = search_image('若井友希')
        #     # 写真送付
        #     i = random.randint(0, len(images) - 1)
        #     send_picture(to, images[i])
        #     send_text(to, "よんだー？")
        # elif req["content"]["text"] == u"すし":
        #     send_text(to, "🍣")
        # else:
        #     # メッセージ送信
        #     i = random.randint(0, len(TALKS) - 1)
        #     send_text(to, TALKS[i])

    # 戻り値は200固定
    return Response(status=200)


def search_image(query):
    bing_url = MICROSOFT['bing_url']
    MS_ACCESS_KEY = MICROSOFT['MS_ACCESS_KEY']

    payload = { '$format': 'json',
            'Query': "'"+query+"'",
            }
    r = requests.get(bing_url, params=payload, auth=('', MS_ACCESS_KEY))

    count = 1
    for item in r.json()['d']['results']:
        image_url = item['MediaUrl']
        image_thumb_url = item['Thumbnail']['MediaUrl']
        root,ext = os.path.splitext(image_url)
        break
    images = [{'origin':image_url, 'thumb':image_thumb_url}]
    return images

def get_send_message(text) :
    chat_url = USER_LOCAL['chat']
    params = {
            'message' : text,
            'key' : USER_LOCAL['key']
            }
    r = requests.get(chat_url, params=params)
    return r.json()['result']

def get_character_text(text) :
    chat_url = USER_LOCAL['character']
    params = {
            'message' : text,
            'character_type' : 'cat',
            'key' : USER_LOCAL_KEY
            }
    r = requests.get(chat_url, params=params)
    return r.json()['result']

def send_text(to, text):
    """
    toに対してテキストを送る
    """
    content = {
            "contentType": 1,
            "toType": 1,
            "text": text
            }
    events(to, content)


def send_picture(to, img):
    """
    toに対して画像を送る
    """
    content = {
            "contentType": 2,
            "toType": 1,
            "originalContentUrl": img["origin"],
            "previewImageUrl": img["thumb"]
            }
    events(to, content)

def events(to, content):
    """
    toに対してデータ(テキスト・画像・動画)を送る
    """
    app.logger.info(content)
    data = {
            "to": to,
            "toChannel": "1383378250",
            "eventType": "138311608800106203",
            "content": content
            }
    r = requests.post(LINE_ENDPOINT + "/v1/events", data=json.dumps(data), headers=HEADERS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=8080)
