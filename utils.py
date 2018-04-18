#define utils 
import numpy as np
import cv2
import math
import pickle 
import json
import time
import copy

class originImg:    
    def __init__(self):  
        self.img = np.zeros(0)
        self.origin_W = 0
        self.origin_H = 0
        self.img_scale = 1
        self.MAX_RESOLUTION = 262144

class debugData:
    def __init__(self, debug_info0):
         self.data = []
         self.debug_info = debug_info0
         self.out_path = ""
         
class mainAlgoData:    
    def __init__(self, _position0, base_data=[], pkl_file="", base_algo="grab_cut"):  
        self.flag = False 
        self.err_msg = "please add rect or reseanable brush first!"  
        self.position = _position0
        self.rect = []
        self.mask2 = np.zeros(0)
        self.algo = base_algo
        self.sub_masks = []
        
        print "grab_cut", base_algo
        if ("grab_cut" == base_algo):
            if pkl_file:  
                with open(pkl_file, 'rb') as f:
                    last_algo = pickle.load(f)
                    print "utils: last_algo is ", last_algo
                    if ("grab_cut" == last_algo):
                        self.mask, self.mask2, self.bgdModel, self.fgdModel, self.img, self.img_scale, self.rect = pickle.load(f)    
                    elif ("SOD" == last_algo):
                        SOD_mask, self.img = pickle.load(f)  
                        self.img_scale = base_data.img_scale
                        self.mask = np.where(SOD_mask>128,1,0).astype('uint8')
                        self.img = cv2.resize(
                            base_data.img,
                            (base_data.origin_W/self.img_scale, base_data.origin_H/self.img_scale),
                            cv2.INTER_CUBIC
                        ) 
                        self.mask = cv2.resize(
                            self.mask,
                            (base_data.origin_W/self.img_scale, base_data.origin_H/self.img_scale),
                            cv2.INTER_CUBIC
                        )
                        self.mask2 = np.where((self.mask>128),255,0).astype('uint8')
                        self.bgdModel = np.zeros((1,65),np.float64)
                        self.fgdModel = np.zeros((1,65),np.float64) 
            else:
                self.img_scale = base_data.img_scale
                self.img = cv2.resize(
                    base_data.img,
                    (base_data.origin_W/self.img_scale, base_data.origin_H/self.img_scale),
                    cv2.INTER_CUBIC
                ) 
                self.mask = np.zeros(self.img.shape[:2],np.uint8)+2
                self.bgdModel = np.zeros((1,65),np.float64)
                self.fgdModel = np.zeros((1,65),np.float64) 
        
        if ("SOD" == base_algo):
            if base_data:
                self.img = base_data.img
                self.mask = np.zeros(0)
            
            
def init_image(filename):
    ori_img = originImg()
    ori_img.img = cv2.imread(filename)
    (ori_img.origin_H, ori_img.origin_W) = (ori_img.img.shape[0], ori_img.img.shape[1]) 
    ori_img.img_scale = int(math.sqrt((ori_img.origin_H * ori_img.origin_W - 1.0) / ori_img.MAX_RESOLUTION)) + 1 \
          if ori_img.origin_H * ori_img.origin_W > ori_img.MAX_RESOLUTION else 1
    
    return ori_img
     
def parse_rect(pos_rect, img_scale):
    unit_rect = [int(s*1.0/(pos_rect[4]*img_scale)+0.5) for s in pos_rect] 
    rect = min(unit_rect[0], unit_rect[2]), min(unit_rect[1], unit_rect[3]), abs(unit_rect[0]-unit_rect[2]), abs(unit_rect[1]-unit_rect[3])     
    return rect


def parse_brush_modifyed(mask, pos_brush, img_scale, this_uuid = ""):
    scales = 1
    rects = [[], []]
    for ss in [0, 1]: #0: minus, 1: plus
        tmp_pos = pos_brush[ss]
        tmp_rect = [] #[row_min, column_min, row_max, column_max]
        tmp_seeds = []   
        for k in xrange(0, len(tmp_pos), 2):                     
            if tmp_pos[k] < 0:
                scales =  1.0 / (img_scale * tmp_pos[k+1])
            else:
                tmp_seeds.append(int(tmp_pos[k]*scales+0.5))
                tmp_seeds.append(int(tmp_pos[k+1]*scales+0.5))
                
            if (k+2>=len(tmp_pos)) or (tmp_pos[k+2]<0):
               # print tmp_seeds
                r, c, h, w = tmp_seeds[1::2], tmp_seeds[::2], mask.shape[0], mask.shape[1]
                radias = max(10, np.sqrt((max(r)-min(r))*(max(r)-min(r)) + (max(c)-min(c))*(max(c)-min(c))))  # the raidas is extened 2 times
               # print np.mean(r), np.mean(c)
                rect = [np.mean(r)-radias, np.mean(c)-radias, np.mean(r)+radias, np.mean(c)+radias]
                t_r = [max(0, rect[0]), max(0, rect[1]), min(h, rect[2]), min(w, rect[3])]
                t_r = [int(s+0.5) for s in t_r]
                 
                if 0==ss:
                    mask[t_r[0]:t_r[2], t_r[1]:t_r[3]] = mask[t_r[0]:t_r[2], t_r[1]:t_r[3]] + np.where(1==mask[t_r[0]:t_r[2], t_r[1]:t_r[3]], 2, 0)
                else:
                    mask[t_r[0]:t_r[2], t_r[1]:t_r[3]] = mask[t_r[0]:t_r[2], t_r[1]:t_r[3]] + np.where(0==mask[t_r[0]:t_r[2], t_r[1]:t_r[3]], 2, 0)
                rects[ss].append(t_r)
                tmp_seeds = []
    
    scales = 1
    for ss in [0, 1]: #0: minus, 1: plus
        tmp_pos = pos_brush[ss]                
        for k in xrange(0, len(tmp_pos), 2):                     
            if tmp_pos[k] < 0:
                scales =  1.0 / (img_scale * tmp_pos[k+1])
                brush_width = int(max(1, -tmp_pos[k]*1.0/img_scale)+0.5)
            else:
                if tmp_pos[k-2] > 0:
                    cv2.line(mask, ( int(tmp_pos[k-2]*scales+0.5), int(tmp_pos[k-1]*scales+0.5) ), \
                      ( int(tmp_pos[k]*scales+0.5), int(tmp_pos[k+1]*scales+0.5) ), ss, brush_width)
    
    print rects
    
    if this_uuid:
        cv2.imwrite('images/user/' + this_uuid + '_brush_in_mask.png', mask*85)   
        
    mask = mask.astype('uint8')        
    return mask, rects

def parse_brush(mask, pos_brush, img_scale, this_uuid = ""):
    scales = 1
    
    for ss in [0, 1]: #0: minus, 1: plus
        tmp_pos = pos_brush[ss]
        for k in xrange(0, len(tmp_pos), 2):
            if tmp_pos[k] < 0:
                scales =  1.0 / (img_scale * tmp_pos[k+1])
                brush_width = int(max(1, -tmp_pos[k]*1.0/img_scale)+0.5)
            else:
                if tmp_pos[k-2] > 0:
                    cv2.line(mask, ( int(tmp_pos[k-2]*scales+0.5), int(tmp_pos[k-1]*scales+0.5) ), \
                      ( int(tmp_pos[k]*scales+0.5), int(tmp_pos[k+1]*scales+0.5) ), ss, brush_width)
    
    if this_uuid:
        cv2.imwrite('images/user/' + this_uuid + '_brush_in_mask.png', mask*85)   
        
    mask = mask.astype('uint8')        
    return mask     
  
#def parse_brush_pos(in_mask, pos_brush, img_scale):
#    scales = 1
#    mask = np.zeros(in_mask.shape)
#    seeds = []
#    for ss in [0, 1]: #0: minus, 1: plus
#        tmp_pos = pos_brush[ss]
#        tmp_seeds = []
#        for k in xrange(0, len(tmp_pos), 2):
#            if tmp_pos[k] < 0:
#                scales =  1.0 / (img_scale * tmp_pos[k+1])
#                brush_width = int(max(1, -tmp_pos[k]*1.0/img_scale)+0.5)
#            else:
#                if tmp_seeds:
#                    if not (tmp_seeds[-1] == [ int(tmp_pos[k+1]*scales+0.5), int(tmp_pos[k]*scales+0.5) ]):
#                        tmp_seeds.append([ int(tmp_pos[k+1]*scales+0.5), int(tmp_pos[k]*scales+0.5) ])
#                else:
#                    tmp_seeds.append([ int(tmp_pos[k+1]*scales+0.5), int(tmp_pos[k]*scales+0.5) ])
#            
#        seeds.append(copy.deepcopy(tmp_seeds))
#    
#    print seeds      
#    return seeds, brush_width     
    
#def parse_rect_brush(mask, position, img_scale, this_uuid = ""):
#    if position[0]:
#        mask = np.zeros(mask.shape[:2],np.uint8) + 0
#        unit_rect = parse_rect(position[0], img_scale)
#        mask[unit_rect[1]:(unit_rect[1]+unit_rect[3]), unit_rect[0]:(unit_rect[0]+unit_rect[2])] = 3
#    
#    scales = 1
#    if len(position[1]) | len(position[2]):            
#        for ss in [0, 1]: #0: minus, 1: plus
#            tmp_pos = position[ss+1]
#            for k in xrange(0, len(tmp_pos), 2):
#                if tmp_pos[k] < 0:
#                    scales =  1.0 / (img_scale * tmp_pos[k+1])
#                    brush_width = int(max(1, -tmp_pos[k]*1.0/img_scale)+0.5)
#                else:
#                    if tmp_pos[k-2] > 0:
#                        cv2.line(mask, ( int(tmp_pos[k-2]*scales+0.5), int(tmp_pos[k-1]*scales+0.5) ), \
#                          ( int(tmp_pos[k]*scales+0.5), int(tmp_pos[k+1]*scales+0.5) ), ss, brush_width)
#    
#    
#    if this_uuid:
#        cv2.imwrite('images/user/' + this_uuid + '_brushrect_in_mask.png', mask*85)   
#        
#    mask = mask.astype('uint8') 
#    return mask

def cut_rect(mask, TH):   
    start = time.time()  
    min_r, max_r, min_c, max_c = mask.shape[0], 0, mask.shape[1], 0
    for i in xrange(mask.shape[0]):
        for j in xrange(mask.shape[1]):
            if mask[i, j]>TH:
                if i < min_r:
                    min_r = i
                if i > max_r:
                    max_r = i
                if j < min_c:
                    min_c = j
                if j > max_c:
                    max_c = j 

    rect = [min_c, min_r, max_c-min_c, max_r-min_r]      
    print "cut rect time:", time.time()-start       
    return rect
    
def write_out_img(algo_data, this_uuid, shape0):
    start = time.time()    
    with open('images/user/'+this_uuid+'_mask.pkl','wb') as f:
        pickle.dump(algo_data.algo, f)
        if ("grab_cut" == algo_data.algo):
            pickle.dump((algo_data.mask, algo_data.mask2, algo_data.bgdModel, algo_data.fgdModel, \
                algo_data.img, algo_data.img_scale, algo_data.rect), f) 
        elif ("SOD" == algo_data.algo): 
            pickle.dump((algo_data.mask, algo_data.img), f)  
            
    print "save pkl time:", time.time()-start 
    tmp_img = algo_data.img*0.8*algo_data.mask2[:,:,np.newaxis]/255.0 + algo_data.img*0.2
    cv2.imwrite('images/user/'+this_uuid + algo_data.algo + '_final_out.png', tmp_img)
    
    for k in xrange(len(algo_data.sub_masks)):
        tmp_mask_url = 'images/user/sub_mask_'+ this_uuid + str(k) + '.png'
        cv2.imwrite(tmp_mask_url, algo_data.sub_masks[k]['mask'])
        algo_data.sub_masks[k]['mask'] = tmp_mask_url
    
    
    start = time.time()   
    algo_data.mask2 = cv2.resize(algo_data.mask2, shape0, cv2.INTER_CUBIC)      
    out_name = this_uuid + '_mask.png'
    cv2.imwrite('images/user/'+out_name, algo_data.mask2)
    print "write time:",  time.time()-start  
    
    return cut_rect(algo_data.mask2, 1)

