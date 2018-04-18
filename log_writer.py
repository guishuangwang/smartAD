import numpy as np
import utils
import cv2
import copy
import os
import pickle 
import json

def write_log_img(img, mask2, mask, path_w_preffix):
    tmp_img = img*0.8*mask2[:,:,np.newaxis]/255.0 + img*0.2 
    cv2.imwrite(path_w_preffix + '_out_image.png', tmp_img)   
    cv2.imwrite(path_w_preffix + '_out_mask.png', mask*85) 

def main_log(algo_data, log_data, stage):
    LOG_PATH, iter_time = log_data.out_path, str(log_data.debug_info[1])
    if log_data.debug_info[0]:
        if ('init' == stage):
            log_data.out_path = os.getcwd()+ "/user_history/" + log_data.debug_info[0] + "/" 
            LOG_PATH = log_data.out_path
            print LOG_PATH
            if '0' == iter_time: #first interaction       
                if not os.path.exists(LOG_PATH):     
                    os.mkdir(LOG_PATH)
                    os.mkdir(LOG_PATH + "user/")
                    os.mkdir(LOG_PATH + "algo/")                     
                    
                cv2.imwrite(LOG_PATH + "user/origin_img.png", log_data.data)
            
            if not os.path.exists(LOG_PATH + "algo/" + iter_time):   
                os.mkdir(LOG_PATH + "algo/" + iter_time)        
            with open(LOG_PATH + "user/" + iter_time + ".pkl", 'wb') as f:
                cv2.imwrite(LOG_PATH + "algo/" + iter_time + '/algo_image.png', algo_data.img) 
                pickle.dump(algo_data.position, f)               
           
            json_data = {}
            json_data['rect'] = algo_data.position[0]
            json_data['m_brush'] = algo_data.position[1]
            json_data['p_brush'] = algo_data.position[2]       
            with open(LOG_PATH + "user/" + iter_time + ".json", 'w') as json_file:
                json_file.write(json.dumps(json_data))
                 
        elif ('rect' == stage):         
            OUT_PATH = LOG_PATH + "algo/" + iter_time
            
            tmp_img = copy.deepcopy(algo_data.img)
            rect = utils.parse_rect(algo_data.position[0], algo_data.img_scale)
            cv2.rectangle(tmp_img, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (0, 0, 255), 2)
            cv2.imwrite(OUT_PATH + '/rect_user.png', tmp_img)
            
            write_log_img(algo_data.img, algo_data.mask2, algo_data.mask, OUT_PATH+"/rect")
            
        elif (('brush_before' == stage) or ('brushrect_before' == stage)): 
            OUT_PATH = LOG_PATH + "algo/" + iter_time            
            tmp_name = stage.split('_')[0]            
            brush_mask = np.where((algo_data.mask==1),1,0) + np.where((algo_data.mask==0), -1, 0)

            cv2.imwrite(OUT_PATH + "/" + tmp_name + "_user.png", \
               algo_data.img+np.ones(algo_data.img.shape)*255*brush_mask[:,:,np.newaxis])
            cv2.imwrite(OUT_PATH + "/" + tmp_name + "_in_mask.png", algo_data.mask*85) 
     
        elif (('brush_after' == stage) or ('brushrect_after' == stage)): 
            OUT_PATH = LOG_PATH + "algo/" + iter_time
            tmp_name = stage.split('_')[0] 
            write_log_img(algo_data.img, algo_data.mask2, algo_data.mask, OUT_PATH+"/"+tmp_name)
        
        elif ('mask_' == stage[:5]):
            OUT_PATH = LOG_PATH + "algo/" + iter_time
            tmp_name = stage.split('_')[1]   
            cv2.imwrite(OUT_PATH + "/" + tmp_name + "_mask.png", algo_data.mask*85)     
                 
        elif ('mask2_' == stage[:6]):  
            OUT_PATH = LOG_PATH + "algo/" + iter_time
            tmp_name = stage.split('_')[1]   
            cv2.imwrite(OUT_PATH + "/" + tmp_name + "_mask2.png", algo_data.mask2)       
            
    return log_data
    
