# -*- coding: utf-8 -*-
import json
import urllib.request
import requests

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template, jsonify

app = Flask(__name__)

slack_token = 'xoxb-503818135714-507655914933-7v7g4cr1mACcyQJXSjFWjHzv'
slack_client_id = '503818135714.506716634864'
slack_client_secret = '503818135714.506716634864'
slack_verification = 'II7FkLo86MUhpTdFmudqDdau'
sc = SlackClient(slack_token)

userid = 'session'

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    reply = get_answer(text, userid)
    keywords = []

    if reply == "bugs":
        keywords.append("Bugs 실시간 음악 차트 Top 10")
        titles = []
        artists = []
        # 여기에 함수를 구현해봅시다.

        sourcecode = urllib.request.urlopen('https://music.bugs.co.kr/').read()
        soup = BeautifulSoup(sourcecode, 'html.parser')
        cnt = 1
        for naver_text in soup.find_all('p', class_="title"):
            titles.append(naver_text.get_text().replace("\n", ""))
        for bugs_text in soup.find_all('p', class_="artist"):
            artists.append(bugs_text.get_text().replace("\n", ""))
        for i in range(1, 11):
            print(titles[i] + "/" + artists[i])
            keywords.append(str(i) + "위 : " + titles[i] + "/" + artists[i])

    else :
        keywords.append("Invalid query")

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        # 추가 =======
        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )
        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

#================================================ dialog 추가 부분
def get_answer(text, user_key):
    data_send = {
        'query': text,
        'sessionId': user_key,
        'lang': 'ko',
    }
    data_header = {
        'Authorization': 'Bearer 4045c167241f43f8929aa4b7eaabca48',
        'Content-Type': 'application/json; charset=utf-8'
    }

    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'
    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)

    if res.status_code != requests.codes.ok:
        return '오류가 발생했습니다.'

    data_receive = res.json()
    return data_receive['result']['fulfillment']['speech']

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['POST', 'GET'])
def webhook():
    content = request.args.get('content')
    userid = 'session'
    return get_answer(content, userid)
#================================================ dialog 추가 부분


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
