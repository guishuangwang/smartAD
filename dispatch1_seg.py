#! /usr/bin/python
# -*- coding: utf-8 -*- #
import uuid
import base64
import json
import os
from tempfile import NamedTemporaryFile

import database as db
import urllib2
import sys
import time
import math
import copy

import utils
import grab_cut_cv
import salience

reload(sys)
print sys.getdefaultencoding()
sys.setdefaultencoding('utf-8') 
#change to your function and init the models files
#from my_py_file.image_classify import my_analyse_func
#my_analyse_func.init()

import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pickle

import mat

def base64_2_img(_str):
    img = base64.decodestring(_str)
    return img

def upload_image(_user_img, callback=None):
    tmp_name = str(uuid.uuid4()) + '.jpg'
#    tmp_name = '49f1ac4a-f471-4fcf-bcfe-244ac1144161.jpg'
#	  tmp_name = 'c5a27715-fcfb-42a4-b767-a49c1d9fcb41.jpg'
    with open('images/user/' + tmp_name, 'wb') as f:
        f.write(_user_img['body'])  
    
    try:
        if not (cv2.imread('images/user/' + tmp_name)): 
            if callback == None:
                return False
            else:
                callback(False)  
    except:
        if callback == None:
            return tmp_name
        else:
            callback(tmp_name)
  
        
def send_interaction(_position, _data_names, debug_info=["", 0], callback=None):
    this_uuid = str(uuid.uuid4());
    print "dispatch1.send_interaction: this_uuid.", this_uuid
    
    base_data = utils.init_image(_data_names[1])
    print "dispatch1.send_interaction: load finish base_data.", base_data.img_scale, base_data.img.shape
    log_data = utils.debugData(debug_info)
    log_data.data = base_data.img
    print "dispatch1.send_interaction: load finish log_data", log_data.debug_info[1]
    
    if ('init' == _data_names[0]):
        print "dispatch1.send_interaction: first time use grab cut"
        algo_data = utils.mainAlgoData(_position, base_data, "", "grab_cut")
        algo_data = grab_cut_cv.grabcut_main(algo_data, log_data)  
        if not algo_data.flag:
            print "dispatch1.send_interaction: first time grab cut failed, use SOD"
            algo_data = utils.mainAlgoData(_position, base_data, "", "SOD")
            algo_data = salience.SOD_main(algo_data, log_data)  
    else:
        print "dispatch1.send_interaction: iterate time use grab cut"
        algo_data = utils.mainAlgoData(_position, base_data, _data_names[2], "grab_cut")
        algo_data = grab_cut_cv.grabcut_main(algo_data, log_data)  
        
   # print "dispatch1.send_interaction: load finish algo_data", algo_data.mask.shape    
             
    if algo_data.flag:   
        out_rect = utils.write_out_img(algo_data, this_uuid, (base_data.origin_W, base_data.origin_H))            
        if callback == None:
            return [algo_data.flag, this_uuid, out_rect, algo_data.sub_masks]
        else:
            callback([algo_data.flag, this_uuid, out_rect, algo_data.sub_masks]) 
    else:
        if callback == None:
            return [algo_data.flag, algo_data.err_msg]
        else:
            callback([algo_data.flag, algo_data.err_msg])    
