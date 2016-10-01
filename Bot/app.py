#-*- coding: utf-8 -*-

from celery_worker import worker
import common.test as tester
from flask import Flask
from flask import Response
from flask import request
import requests
import json  
from manager import redis_manager
from manager import db_manager
from common import static
import datetime
from common import util
import time
import base64

# test before running flask
# tester.run_unit_test()

app = Flask(__name__)

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def home():

    url = ("https://slack.com/oauth/authorize?client_id="
        +key['slackapp']['client_id']
        +"&scope=team:read+channels:read+channels:history+chat:write:bot+channels:read+users:read")


    html = "<html> <body> <a href='"+url+"'>슬랙 연결</a> </body> </html>"

    return html

@app.route('/slack/oauth', methods = ['GET'])
def slack_oauth():
    code = request.args.get('code')
    r = requests.post("https://slack.com/api/oauth.access", 
        data = {
            'client_id'     : key['slackapp']['client_id'], 
            'client_secret' : key['slackapp']['client_secret'], 
            'code'          : code
        }
    )

    response = json.loads(r.text)

    print(response)
    query = (
        "INSERT INTO TEAM " 
        "(`team_id`, `team_name`, `team_joined_time`, `team_access_token`)"
        "VALUES"
        "('{0}', '{1}', '{2}', '{3}')"
        .format(response['team_id'], 
                base64.b64encode(bytes(response['team_name'], 'utf-8')).decode("utf-8"), 
                datetime.date.fromtimestamp(time.time()),
                response['access_token']
                )
    )
    conn = db_manager.engine.connect()
    trans = conn.begin()
    conn.execute(query)
    trans.commit()
    print(query)
    return 'auth success' + response['access_token']

@app.route('/slack/event', methods = ['POST'])
def slack_event():
    payload = request.get_data().decode()
    data = json.loads(payload) 

    print(data)
    
    
    response = {}

    if data['type'] == 'url_verification':         
        response['challenge'] = data['challenge']
        
    elif data['type'] == 'event_callback':
        #sql = "INSERT into GAME_INFO values(%s,%s,%s,%i,%s,%s,%i)"

        # db_manager.curs.execute(sql, ("gameId","teamId","channel_id",4,"start_tiem","end_time",3))


        # if(redis_manager.redis_client.get("hasTeam" + data['team_id'])==None){
        #     sql = "insert into TEAM values(%s,%s,%s)"
        #     curs.execute(sql)

        #     # 데이타 Fetch
        #     rows = curs.fetchall()
        #     print(rows)  # 전체 rows
        #     # print(rows[0])  # 첫번째 row: (1, '김정수', 1, '서울')
        #     # print(rows[1])  # 두번째 row: (2, '강수정', 2, '서울')

        #     # Connection 닫기
        #     conn.close()    
        # }
        # worker.delay(data['event'])
        eventData = data['event']
        #eventData에 팀 아이디 추
        eventData["team_id"] = data['team_id']

        if 'subtype' in data['event']:
            subtype = eventData['subtype']
        else:
            subtype = None

        # print(eventData)
        if eventData['type'] == "message" and subtype == None or subtype != 'bot_message' :

            status_channel = redis_manager.redis_client.get("status_" + eventData["channel"])
            # redis_manager.redis_client.set("status_" + eventData["channel"], static.GAME_STATE_IDLE)
            # print('status_channel => '+ㄴㅅstatic.GAME_STATE_IDLE)

            # 게임이 플레이중이라면
            if status_channel == static.GAME_STATE_PLAYING :
                print('playing')
                worker.delay(eventData)

            # 게임 플레이중이 아니라면
            elif status_channel == static.GAME_STATE_IDLE or status_channel == None :
                print('commend')
                if eventData["text"] == static.GAME_COMMAND_START:
                    print('.start')
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_RANK:
                    print('.rank')
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_MY_RANK:
                    print('.myrank')
                    worker.delay(eventData)
                elif eventData["type"] == "channel_joined":
                    print('others')
                    worker.delay(eventData)

    return json.dumps(response)



ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')

app.run(host='0.0.0.0', debug='True', port = 20000, ssl_context = ssl_context)
conn = engine.connect()
trans = conn.begin()
conn.execute(text("insert into PROBLEM (problem_id,problem_text) values(%i,%s) ",0,"hello").execution_options(autocommit=False))
trans.commit()
conn.close()
