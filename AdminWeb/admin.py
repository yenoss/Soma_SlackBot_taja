# -*- coding: utf-8 -*-

import sys 
sys.path.append("../")

import sys
import os

from flask import redirect, url_for
from Common.manager import db_manager

# from flask_cors import CORS, cross_origin
from Common.slackapi import SlackApi

from flask import Flask
from flask import request
# from flask import render_template

import json
import time
import logging
import static

logging.basicConfig(filename='log.log', level=logging.DEBUG)

app = Flask(__name__, static_url_path='')
# CORS(app)



# 라우트스 안에 멤버 메소드 콜

from route import member
from route import dashboard
from Common import util
import datetime

member_view = member.Members.as_view('member')

app.add_url_rule('/member/getAllUser', defaults={'types': 'getAllUser'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getSpecificUserInfoById', defaults={'types': 'getSpecificUserInfoById'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getSpecificUserGameResultById', defaults={'types': 'getSpecificUserGameResultById'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getAllProblem', defaults={'types': 'getAllProblem'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getSpecificProblemInfoById', defaults={'types': 'getSpecificProblemInfoById'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getAllTeam', defaults={'types': 'getAllTeam'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getTeamInfo', defaults={'types': 'getTeamInfo'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getChannelInfo', defaults={'types': 'getChannelInfo'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getAllChannel', defaults={'types': 'getAllChannel'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getAllGameResult', defaults={'types': 'getAllGameResult'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getAllGame', defaults={'types': 'getAllGame'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getGameInfo', defaults={'types': 'getGameInfo'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getGameResultIDS', defaults={'types': 'getGameResult'},
                 view_func=member_view, methods=['GET', ])

app.add_url_rule('/member/getTest', defaults={'types': 'getTest'},
                 view_func=member_view, methods=['GET', ])

dashboard_view = dashboard.DashBoards.as_view('dashBoard')
app.add_url_rule('/dashBoard/getIndicator', defaults={'types': 'getIndicator'},
                 view_func=dashboard_view, methods=['GET', ])

app.add_url_rule('/dashBoard/getInActiveGraph', defaults={'types': 'getInActiveGraph'},
                 view_func=dashboard_view, methods=['GET', ])

app.add_url_rule('/dashBoard/getActiveGraph', defaults={'types': 'getActiveGraph'},
                 view_func=dashboard_view, methods=['GET',])

app.add_url_rule('/dashBoard/getTopTwenty', defaults={'types': 'getTopTwenty'},
                 view_func=dashboard_view, methods=['GET',])


@app.route('/member/sendNotification',methods=['POST'])
def sendNotification():
    notiInfo = request.form['notiInfo']
    try:
        conn = db_manager.engine.connect()
        trans = conn.begin()
        result = conn.execute(
            "select *from TEAM inner join USER on TEAM.team_id = USER.team_id"
        )
        trans.commit()
        conn.close()    
        
        rows =util.fetch_all_json(result)
        for row in rows:        
            slackApi = SlackApi(row['team_access_token'])
            slackBotApi = SlackApi(row['team_bot_access_token'])
            slackBotApi.chat.postMessage(
                {
                    'channel' : row['user_id'],
                    'as_user'   : 'true',
                    'text' : notiInfo
                }
            ) 
        return json.dumps({'success': True,'suc_cnt':len(rows)}), 200, {'ContentType': 'application/json'}

    except Exception as e:        
        return json.dumps({'success': False,'reason':str(e)}), 400, {'ContentType': 'application/json'}





@app.route('/member/newProblem', methods=['POST'])
def newProblem():
    problem_text = request.form['problem_text']
    problem_difficulty = request.form['problem_difficulty']

    conn = db_manager.engine.connect()
    trans = conn.begin()
    conn.execute(
        "INSERT INTO `slackbot`.`PROBLEM` (`problem_text`, `validity`, `difficulty`) VALUES (%s, %s, %s);",
        (problem_text, 1, problem_difficulty)
    )
    trans.commit()
    conn.close()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/member/editProblem', methods=['POST'])
def editProblem():
    validity = request.form['validity']
    difficulty = request.form['difficulty']
    problem_id = request.form['problem_id']

    conn = db_manager.engine.connect()
    trans = conn.begin()
    conn.execute(
        "UPDATE `slackbot`.`PROBLEM` SET `validity`=%s, `difficulty`=%s WHERE `problem_id`=%s;",
        (validity, difficulty, problem_id)
    )
    trans.commit()
    conn.close()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/manager/teamInfo', methods=['POST'])
def manager_team_info():
    jsonObject = {
        'data': [
            {'team_id': '1',
             'team_name': '333'},
            {'team_id': '1',
             'team_name': '333'}
        ]
    }
    return json.dumps(jsonObject)


@app.route('/', methods=['GET'])
def redirect_to_index():
    return redirect(url_for('static', filename='indexx.html'))


if __name__ == '__main__':
    # ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')

    app.run(host='0.0.0.0', port=10001, debug=True)

