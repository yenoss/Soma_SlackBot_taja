# #-*- coding: utf-8 -*-
import sys 
sys.path.append("../")

import uuid
import korean
import threading
from functools import wraps
from Common.slackapi import SlackApi
from Common.manager import db_manager
import random


# 팀별 SlackApi 객체 생성
def init_slackapi(teamId):

#    #conn = db_manager.session.connection()
    result = fetch_all_json(db_manager.query(
            "SELECT team_access_token FROM TEAM "
            "WHERE `team_id`   =  %s " 
            "LIMIT 1"
            ,
            (teamId,)
        ) 
    )
#    #conn.close()
    print(result)
    slackApi = SlackApi(result[0]['team_access_token'])
    return slackApi

def get_bot_id(teamId):
    bot_id = fetch_all_json(db_manager.query(
        "SELECT bot_id "
        "FROM TEAM "
        "WHERE "
        "team_id = %s "
        "LIMIT 1 ",
        (teamId,)
    ))[0]['bot_id']
    return bot_id

# delay
def delay(delay=0.):
   def wrap(f):
       @wraps(f)
       def delayed(*args, **kwargs):
           timer = threading.Timer(delay, f, args=args, kwargs=kwargs)
           timer.start()
       return delayed
   return wrap

def split_character(string):
    response = ""
    for char in string:
        if korean.hangul.is_hangul(char):
            response += ''.join(korean.hangul.split_char(char))
        else:
            response += char
    return response

def get_edit_distance(string1, string2):

    s1 = split_character(string1)
    s2 = split_character(string2)

    d = [[0 for col in range(len(s2) + 1)] for row in range(len(s1) + 1)]

    for i in range(0, len(s1) + 1):
        d[i][0] = i

    for i in range(0, len(s2) + 1):
        d[0][i] = i

    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min([d[i - 1][j - 1] + 1, d[i][j - 1] + 1, d[i - 1][j] + 1])

    return d[len(s1)][len(s2)]

def get_accuracy (s, distance):
    l = len(split_character(s))
    return ((l - distance) / l)

def get_speed (s, time):
    l = len(split_character(s))
    return l / (time/1000)*60*1000

#accur : 0.0 ~ 1.0
#speed : 0.0 ~ 400(or more)
#score : 0.0 ~ 400(or more)
def get_score(speed, accur):
    conv_accur = pow(accur, 2)
    score = conv_accur * speed

    return score


def generate_game_id ():
    return uuid.uuid4()


def fetch_all_json(result):
  lis = []

  for row in result.fetchall():
    i =0
    dic = {}  
    
    for data in row:
      # if(len(result.keys())
      # print(len(result.keys()))
      # print(i)
      # print(data)
      dic[result.keys()[i]]= data
      if i == len(row)-1:
        lis.append(dic)

      i=i+1
  return lis


def get_problems():

    # 우선 문제 Set들을 가져와서 Validity가 1인 문제 하나를 랜던하게 id를 반환

    texts = {}

    result = db_manager.engine.connect().execute(
        "SELECT problem_id, problem_text, difficulty "
        "FROM PROBLEM "
        "WHERE validity = %s",
        1
    )

    rows = fetch_all_json(result)

    for row in rows:
        texts[row['problem_id']] = row['problem_text']

    return texts

#랜덤한 값출력해주는 함수. 
#자주쓰는 함수임으로 등록.
# getRandomValue(1,10) 이면 1~10까지의값중 하나를 선택해 랜덤하게 리턴해준다.
def getRandomValue(to,frm):
    return random.randrange(to,frm+1)

