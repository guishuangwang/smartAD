#-*- coding:utf-8 -*-
import uuid
import base64
import json
import os
from tempfile import NamedTemporaryFile

import database as db

#change to your function and init the models files
#from my_py_file.image_classify import my_analyse_func
#my_analyse_func.init()

def base64_2_img(_str):
    img = base64.decodestring(_str)
    return img

cur_path = os.path.dirname(__file__)
__UPLOADS__ = os.path.join(cur_path,'./uploads/')

def generator_file(file,options,bgimg,callback=None):
    _id = db.newTask()

    #begin generator with `_id` in background
    #step 1: build images
    #....
    #db.updateStatus(_id,'start','gotimg')
    #step 2: train models
    #...
    #db.updateStatus(_id,'gotimg','finish')

    data = {'res':0,'id':_id,'status':'start'}
    if callback == None:
        return data
    else:
        callback(data)

def get_list(callback=None):
    data = {"id_list": ["1.id", "2.id"]}   
    if callback == None:
        return data
    else:
        callback(data)
    

def generator_words(words,options,bgimg,callback=None):

    _id = db.newTask()
    print json.dumps(options)

    #begin generator with `_id` in background
    #step 1: build images
    #....
    #db.updateStatus(_id,'start','gotimg')
    #step 2: train models
    #...
    #db.updateStatus(_id,'gotimg','finish')

    data = {'res':0,'id':_id,'status':'start'}
    if callback == None:
        return data
    else:
        callback(data)

def checkStatus(_missionid,callback=None):
    task = db.checkTask(_missionid)
    status = task['status']
    url = task.get('url')
    data = {'res':0,'id':_missionid,'status':status,'url':url}
    if callback == None:
        return data
    else:
        callback(data)

def getTasks(callback=None):
    tasks=db.findAll()

    data = {'res':0,'tasks':tasks}
    if callback == None:
        return data
    else:
        callback(data)


def analyse(img_path):
    response_data = {}
    try:
        #scores = my_analyse_func.process(img_path)
        scores = 0.0
        response_data['result'] = 0
        response_data['probability'] = float('%.3f'%scores)
        if scores >= 0.5:
            response_data['analyse'] = 1
            response_data["message"] = 'porn'
        else:
            response_data["analyse"] = 0
            response_data["message"] = 'normal'
    except Exception as e:
        print 'exception:',e
        response_data["result"] = 1
        response_data['probability'] = float('%.3f'%float(0))
        response_data["analyse"] = 2
        response_data["message"] = 'unsure'
    return response_data
