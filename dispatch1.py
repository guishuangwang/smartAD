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

reload(sys)
print sys.getdefaultencoding()
sys.setdefaultencoding('utf-8') 
#change to your function and init the models files
#from my_py_file.image_classify import my_analyse_func
#my_analyse_func.init()

import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def base64_2_img(_str):
    img = base64.decodestring(_str)
    return img

def check_index(index, min_val, max_val, default_val = 0):
    out_index = default_val
    
    try:
        out_index = int(index)
    except:
        print 'type error! use default value ' + str(out_index)
    
    out_index = min(max(out_index, min_val), max_val)

    return out_index

cur_path = os.path.dirname(__file__)
__UPLOADS__ = os.path.join(cur_path,'./uploads/')


def get_list(list_in, callback=None):
    if callback == None:
        return list_in
    else:
        callback(list_in)
        

def generate_poster(main_poster, poster_buffer, callback=None):
    bg_img = cv2.imread(main_poster[0]['path'])
    sp = bg_img.shape
    print sp
    poster_height = poster_buffer[1]
    scale = poster_height * 1.0 / sp[0]
    poster_width = int(0.5 + scale * sp[1])
    
    print poster_height, poster_width
    #out_img = cv2.resize(bg_img, (poster_width, poster_height), interpolation=cv2.INTER_CUBIC)
    out_img = cv2.resize(bg_img, (poster_width, poster_height))
   
    for tmp_layer in main_poster[1:]:
        if 'image' == tmp_layer['type']:
            tmp_img = cv2.imread(tmp_layer['path'], cv2.IMREAD_UNCHANGED)
            
            tmp_alpha = float(tmp_layer['alpha'])
            print tmp_alpha
            rect = [int(tmp_layer['position'][1]*poster_height+0.5), int(tmp_layer['position'][0]*poster_width+0.5), \
                    int(tmp_layer['position'][3]*poster_height+0.5), int(tmp_layer['position'][2]*poster_width+0.5)]
                    
          #  tmp_img = cv2.resize(tmp_img, (rect[3]-rect[1], rect[2]-rect[0]), interpolation=cv2.INTER_CUBIC)            
            tmp_img = cv2.resize(tmp_img, (rect[3]-rect[1], rect[2]-rect[0])) 
            
            if tmp_img.shape[2] < 4:
                out_img[rect[0]:rect[2], rect[1]:rect[3], :] = out_img[rect[0]:rect[2], rect[1]:rect[3], :] * (1.0 - tmp_alpha) + tmp_img * tmp_alpha
            elif 4 == tmp_img.shape[2]:
                whole_alpha = (tmp_alpha * tmp_img[:, :, 3]) / 255.0
                for k in xrange(3):
                    out_img[rect[0]:rect[2], rect[1]:rect[3], k] = out_img[rect[0]:rect[2], rect[1]:rect[3], k] * (1.0 - whole_alpha) \
                        + tmp_img[:, :, k] * whole_alpha
        
        elif 'text' == tmp_layer['type']:
            out_img = Image.fromarray(out_img)
            draw = ImageDraw.Draw(out_img)
            font0 = ImageFont.truetype(tmp_layer['font'],  tmp_layer['size'])
             
            text_color = tmp_layer['color'][0], tmp_layer['color'][1], tmp_layer['color'][2]
            c, r = int(tmp_layer['position'][0]*poster_width+0.5), int(tmp_layer['position'][1]*poster_height+0.5)
           
            out_text = ''
            with open(tmp_layer['path']) as f:
                while True:
                    line = f.readline()
                    if line:
                        out_text += line    
                    else:
                        break;
            
            draw.text((c, r), out_text, text_color, font=font0)
            out_img = np.array(out_img)    
             
    cv2.imwrite(poster_buffer[0], out_img)
    
    if callback == None:
        return poster_buffer[0]
    else:
        callback(poster_buffer[0])

def load_poster(_id, callback=None):
    data = []
    with open("Models/psd1_txt1.txt") as f:
        txts = f.readlines();
    
    if '1.id' == _id:
         data.append({"layer": 0, "type": "image", "path": "Models/demo_bg.png",  "alpha": 1, "position": [0, 0, 1, 1]})
         data.append({"layer": 1, "type": "image", "path": "Models/p1.png",  "alpha": 1, "position": [0.2266, 0.4199, 0.7734, 0.7520]})
         data.append({"layer": 2, "type": "image", "path": "Models/P2.png",  "alpha": 1, "position": [0.36979, 0.08789, 0.6302, 0.38086]})
         data.append({"layer": 3, "type": "image", "path": "Models/p3.png",  "alpha": 1, "position": [0.34115, 0.12988, 0.3984, 0.33887]})
         data.append({"layer": 4, "type": "image", "path": "Models/P4.png",  "alpha": 1, "position": [0.35156, 0.87305, 0.6490, 0.93164]})
         data.append({"layer": 5, "type": "text",  "text": txts[0].rstrip().decode("gb2312"), "ver": 0, "color": "(246,180,110)", \
                      "position": [0.3125, 0.78125, 0.313, 0.782], "font": txts[1].rstrip().decode("gb2312"), "size": 28})
         data.append({"layer": 6, "type": "text",  "text": txts[2].rstrip().decode("gb2312"), "ver": 1, "color": "(25,25,25)", \
                      "position": [0.3542, 0.1377, 0.3854, 0.3311], "font": txts[3].rstrip().decode("gb2312"), "size": 19})
         data.append({"layer": 7, "type": "text",  "text": txts[4].rstrip().decode("gb2312"), "ver": 1, "color": "(254,254,254)", \
                       "position": [0.5234375,  0.09375, 0.59375, 0.375], "font": txts[5].rstrip().decode("gb2312"), "size": 42})
         data.append({"layer": 8, "type": "text",  "text": txts[6].rstrip().decode("gb2312"), "ver": 1, "color": "(254,254,254)", \
                       "position": [0.432, 0.09375, 0.50260, 0.375], "font": txts[7].rstrip().decode("gb2312"), "size": 42})
#       data.append({"layer": 9, "type": "text",  "text": txts[8].rstrip().decode("gb2312"), "ver": 0, "color": "(192,192,0)", \
#                    "position": [0, 0, 0.2, 0.2], "font": txts[9].rstrip().decode("gb2312"), "size": 30})
                      
#        data.append({"layer": 0, "type": "image", "path": "Models/psd1_layer1.png",  "alpha": 1, "position": [0, 0, 1, 1]})
#        data.append({"layer": 1, "type": "image", "path": "Models/psd1_layer2.png",  "alpha": 1, "position": [0.55, 0.17, 0.93, 0.88]})
#        data.append({"layer": 2, "type": "image", "path": "Models/psd1_layer3.png",  "alpha": 1, "position": [0.63, 0.28, 0.92, 0.74]})
#        data.append({"layer": 3, "type": "text",  "text": "this",  \
#                             "color": [63, 50, 47], "position": [0.06, 0.18, 0.3, 0.3], "font": "Models/arial.ttf", "size": 56})
#        data.append({"layer": 4, "type": "text",  "text": " that",  \
#                             "color": [63, 50, 47], "position": [0.2, 0.4, 0.5, 0.5], "font": "Models/arial.ttf", "size": 56})
#        data.append({"layer": 5, "type": "text",  "text": "end",  \
#                             "color": [48, 181, 92], "position": [0.05, 0.63, 0.3, 0.8], "font": "Models/arial.ttf", "size": 20})
# 

    
#        data.append({"layer": 0, "type": "image", "path": "Models/psd1_layer1.jpg",  "alpha": 1, "position": [0, 0, 1, 1]})
#        data.append({"layer": 1, "type": "image", "path": "Models/psd1_layer2.jpg",  "alpha": 0.5, "position": [0.1, 0.1, 0.3, 0.3]})
#    #    data.append({"layer": 2, "type": "text",  "path": "Models/psd1_txt1.txt",  \
#     #                "color": [255, 0, 0], "position": [0.4, 0.1], "font": "Models/arial.ttf", "size": 20})
#        data.append({"layer": 2, "type": "text",  "text": "this",  \
#                     "color": [255, 0, 0], "position": [0.4, 0.1, 0.7, 0.4], "font": "Models/arial.ttf", "size": 20})
#        data.append({"layer": 3, "type": "image", "path": "Models/psd1_layer3.png",  "alpha": 0.8, "position": [0.7, 0.7, 0.9, 0.9]})        
    elif '2.id' == _id:
          data.append({"layer": 0, "type": "image", "path": "Models/psd2_layer1.png",  "alpha": 1, "position": [0, 0, 1, 1]})
          data.append({"layer": 1, "type": "image", "path": "Models/psd2_layer2.png",  "alpha": 1, "position": [0.1, 0.1, 0.92, 0.92]})
          data.append({"layer": 2, "type": "text",  "text": "dsgd",  \
                               "color": [255, 255, 255], "position": [0.38, 0.95], "font": "Models/arial.ttf", "size": 41})
          data.append({"layer": 3, "type": "text",  "text": " 2018sdg",  \
                               "color": [255, 255, 255], "position": [0.3, 0.7], "font": "Models/arial.ttf", "size": 41})
#        data.append({"layer": 0, "type": "image", "path": "Models/psd2_layer1.jpg", "alpha": 1, "position": [0, 0, 1, 1]})
#     #   data.append({"layer": 1, "type": "text",  "path": "Models/psd2_txt1.txt", \
#     #                 "color": [0, 0, 255], "position": [0.5, 0.1], "font": "Models/arial.ttf", "size": 20})  
#        data.append({"layer": 1, "type": "text",  "text": "that", \
#                     "color": [0, 0, 255], "position": [0.5, 0.1, 0.6, 0.2], "font": "Models/arial.ttf", "size": 20})  
#     #   data.append({"layer": 2, "type": "text",  "path": "Models/psd2_txt2.txt", \
#     #                 "color": [0, 255, 255], "position": [0.4, 0.8], "font": "Models/fzstk.ttf", "size": 30})  
#        data.append({"layer": 2, "type": "text",  "text": "test2", \
#                      "color": [0, 255, 255], "position": [0.4, 0.8, 0.7, 0.9], "font": "Models/fzstk.ttf", "size": 30})  
    elif '3.id' == _id:
        data.append({"layer": 0, "type": "image", "path": "Models/psd3_layer1.jpg", "alpha": 1, "position": [0, 0, 1, 1]})
        data.append({"layer": 1, "type": "image", "path": "Models/psd3_layer2.png", "alpha": 1, "position": [0, 0.5, 1, 0.8]})
    elif '4.id' == _id:
        data.append({"layer": 0, "type": "image", "path": "Models/psd4_layer3.jpg", "alpha": 1, "position": [0, 0, 1, 1]})
        data.append({"layer": 1, "type": "image", "path": "Models/psd4_layer2.jpg", "alpha": 1, "position": [0.1, 0.2, 0.4, 0.8]})
        data.append({"layer": 2, "type": "image", "path": "Models/psd4_layer1.jpg", "alpha": 0.8, "position": [0.6, 0.3, 0.9, 0.8]})
        data.append({"layer": 3, "type": "image", "path": "Models/psd2_layer1.jpg", "alpha": 0.8, "position": [0, 0, 1, 1]})
        data.append({"layer": 4, "type": "image", "path": "Models/psd1_layer2.jpg", "alpha": 0.8, "position": [0.4, 0.3, 0.7, 0.8]})
     #   data.append({"layer": 2, "type": "text",  "path": "Models/psd2_txt1.txt", \
       #               "color": [255, 0, 0], "position": [0.5, 0.2], "font": "Models/arial.ttf", "size": 35})  
      #  data.append({"layer": 3, "type": "image", "path": "Models/psd4_layer3.jpg", "alpha": 0.8, "position": [0.6, 0.3, 0.9, 0.8]})
   
    if callback == None:
        return data
    else:
        callback(data)


def insert_layer(main_poster, _user_image_name, _user_layer_index, callback=None):
    ins_layer_index = check_index(_user_layer_index, 0, len(main_poster), len(main_poster))   
        
    ins_layer = {"layer": ins_layer_index, "path": _user_image_name, "type": "image",  "alpha": 0.8, "position": [0.25, 0.25, 0.75, 0.75]}
    main_poster.insert(ins_layer_index, ins_layer)
    for k in xrange(ins_layer_index+1, len(main_poster)):
        main_poster[k]['layer'] += 1
    
    if callback == None:
        return main_poster
    else:
        callback(main_poster)

def modify_layer(main_poster, params, callback=None):
    if params.has_key("layer"):
        layer_index = check_index(params["layer"], 0, len(main_poster), -1) 
        if layer_index >= 0:
            for k, v in params.items():
                print k, v
                if main_poster[layer_index].has_key(k):
                    main_poster[layer_index][k] = v
    
    if callback == None:
        return main_poster
    else:
        callback(main_poster)

def upload_image(_user_img, callback=None):
    tmp_name = 'Models/user/' + str(uuid.uuid4()) + '.jpg'
    with open(tmp_name, 'wb') as f:
        f.write(_user_img['body'])  
    
    if callback == None:
        return tmp_name
    else:
        callback(tmp_name)



