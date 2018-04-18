import numpy as np
import utils
import cv2
import copy
import os
import pickle 
import json
import time
import mat
import salience
import log_writer

#from methods import RegionGrowing
#from scipy import ndimage
#import utilities

def matting(img, mask2, method = "guided"):
    '''
    mask2 is 0 and 255
    img is 0-255
    support method: disable, guided, knn
    '''
    mask3 = (mask2>128).astype(np.float64)
    out = mat.matte(img, mask3, method)
    return (out * 255).astype('uint8')

def grabcut_main(algo_data, log_data):
    _position = algo_data.position
    
    log_data = log_writer.main_log(algo_data, log_data, 'init')
    
#    if algo_data.position[0]:
#        algo_data.rect = utils.parse_rect(algo_data.position[0], algo_data.img_scale)
#        
#    algo_data = rectbrush_grabcut(algo_data, log_data) 

    if _position[0]:
        algo_data = rect_grabcut(algo_data, log_data)
        
    if len(_position[1]) | len(_position[2]):  
        #algo_data = brush_region_grow(algo_data, log_data)
        algo_data = mask_grabcut(algo_data, log_data)
        
    print "grab_cut_cv: matting"    
    if algo_data.flag:
        algo_data.mask2 = matting(algo_data.img, algo_data.mask2)
        algo_data.mask = np.where((algo_data.mask2>128),1,0).astype('uint8')
        log_data = log_writer.main_log(algo_data, log_data, 'mask2')
        
    return algo_data

def rect_grabcut(algo_data, log_data=None): 
    rect = utils.parse_rect(algo_data.position[0], algo_data.img_scale)
    start = time.time()
    print "grab_cut_cv: grab cutting rect", rect
    cv2.grabCut(algo_data.img, algo_data.mask, rect,algo_data.bgdModel, algo_data.fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    algo_data.mask2 = np.where((algo_data.mask==2)|(algo_data.mask==0),0,1).astype('uint8')*255
    print "grab_cut_cv: grab cut rect time is:",  time.time()-start 
    
    if log_data:
        log_data = log_writer.main_log(algo_data, log_data, 'rect')
    
    algo_data.flag = True 
    return algo_data

#def brush_region_grow(algo_data, log_data=None):
#    seeds, brush_width  = utils.parse_brush_pos(algo_data.mask, algo_data.position[1:3], algo_data.img_scale)
#    print seeds[1]
#    
#    if log_data:
#        log_data = log_writer.main_log(algo_data, log_data, 'mask2_before_m')            
#    image_array = utilities.rgb_to_gray_scale_conversion(copy.deepcopy(algo_data.img))    
#    mask_m = RegionGrowing().region_growing(image_array, seeds[0], 0.5, 50)
#    algo_data.mask2 = algo_data.mask2 - np.where((mask_m>128) & (algo_data.mask2>128), 255, 0)
#
#    if log_data:
#        log_data = log_writer.main_log(algo_data, log_data, 'mask2_before_p')    
#    image_array = utilities.rgb_to_gray_scale_conversion(copy.deepcopy(algo_data.img))   
#    mask_p =RegionGrowing().region_growing(image_array, seeds[1], 0.5, 50) 
#    algo_data.mask2 = algo_data.mask2 + np.where((mask_p>128) & (algo_data.mask2<128), 255, 0)
#    
#    if log_data:
#        log_data = log_writer.main_log(algo_data, log_data, 'mask2_after') 
#    algo_data.flag = True
#    return algo_data
    
def mask_grabcut(algo_data, log_data=None):
    #algo_data.mask = utils.parse_brush(algo_data.mask, algo_data.position[1:3], algo_data.img_scale)
    algo_data.mask, rects = utils.parse_brush_modifyed(algo_data.mask, algo_data.position[1:3], algo_data.img_scale)
    
    if log_data:
        log_data = log_writer.main_log(algo_data, log_data, 'brush_before')
        
    if (np.sum(algo_data.mask==0)+np.sum(algo_data.mask==2) > 0) and (np.sum(algo_data.mask==1)+np.sum(algo_data.mask==3) > 0):
        start = time.time() 
        print "grab_cut_cv: grab cutting brush"  
        #old_mask = copy.deepcopy(algo_data.mask)
        cv2.grabCut(algo_data.img,algo_data.mask,None,algo_data.bgdModel,algo_data.fgdModel,5,cv2.GC_INIT_WITH_MASK)
        
#        for ss in [0, 1]:
#            for tmp_rect in rects[ss]:
#                old_mask[tmp_rect[0]:tmp_rect[2], tmp_rect[1]:tmp_rect[3]] = \
#                  copy.deepcopy(algo_data.mask[tmp_rect[0]:tmp_rect[2], tmp_rect[1]:tmp_rect[3]])
#        
#        algo_data.mask = copy.deepcopy(old_mask)
        
        algo_data.mask2 = np.where((algo_data.mask==2)|(algo_data.mask==0),0,1).astype('uint8')*255
        
        print "grab_cut_cv: grab cut brush time is", time.time()-start 
        algo_data.flag = True
        
        if log_data:
            log_data = log_writer.main_log(algo_data, log_data, 'brush_after')
    else:
        algo_data.err_msg = ""
        if (np.sum(algo_data.mask==0)+np.sum(algo_data.mask==2) == 0):
            algo_data.err_msg += "please add back ground brush! "
        if (np.sum(algo_data.mask==1)+np.sum(algo_data.mask==3) == 0):
            algo_data.err_msg += "please add fore ground brush!"   
        algo_data.flag = False
        
#    ker = np.ones((10,10)) / 100.0
#    mask2 = cv2.filter2D(mask2, -1, ker)   
    return algo_data  

#def modify_mask(algo_data, log_data=None):
#    old_mask, edit_rect = None, None
#    if (not []==algo_data.position[2]) and (not []==algo_data.rect):
#        old_mask = copy.deepcopy(algo_data.mask)
#        
#        tmp_mask = np.zeros(algo_data.mask.shape) + 3
##        unit_rect = algo_data.rect
##        tmp_mask[unit_rect[1]:(unit_rect[1]+unit_rect[3]), unit_rect[0]:(unit_rect[0]+unit_rect[2])] = \
##            copy.deepcopy(algo_data.mask[unit_rect[1]:(unit_rect[1]+unit_rect[3]), unit_rect[0]:(unit_rect[0]+unit_rect[2])])
#        tmp_mask = utils.parse_brush(tmp_mask, [[], algo_data.position[2]], algo_data.img_scale)
#        
#        if log_data:
#            log_data = log_writer.main_log(algo_data, log_data, 'mask_before_modify')
#        
##        tmp_bgdModel, tmp_fgdModel = copy.deepcopy(algo_data.bgdModel), copy.deepcopy(algo_data.fgdModel)
##        cv2.grabCut(algo_data.img, tmp_mask, None, tmp_bgdModel, tmp_fgdModel, 1, cv2.GC_INIT_WITH_MASK)   
##        algo_data.mask = (algo_data.mask + np.where(((3==tmp_mask) & (0==algo_data.mask)), 2, 0)).astype('uint8')
#        
#        rc = np.where(tmp_mask==1)
#        edit_rect = [np.min(rc[0]), np.min(rc[1]), np.max(rc[0]), np.max(rc[1])]
#        tmp_h, tmp_w, max_h, max_w = edit_rect[2]-edit_rect[0], edit_rect[3]-edit_rect[1], algo_data.mask.shape[0], algo_data.mask.shape[1]
#        edit_rect = [max(0, edit_rect[0]-tmp_h/2), max(0, edit_rect[1]-tmp_w/2), min(max_h, edit_rect[2]+tmp_h/2), min(max_w, edit_rect[3]+tmp_w/2)]
#        print edit_rect
#        edit_rect = [int(s) for s in edit_rect]
#        algo_data.mask[edit_rect[0]:edit_rect[2], edit_rect[1]:edit_rect[3]] = (algo_data.mask[edit_rect[0]:edit_rect[2], edit_rect[1]:edit_rect[3]]     + np.where((0==algo_data.mask[edit_rect[0]:edit_rect[2], edit_rect[1]:edit_rect[3]]), 2, 0)).astype('uint8')
#           
#        if log_data:
#            log_data = log_writer.main_log(algo_data, log_data, 'mask_after_modify')
#    
#    return algo_data.mask, old_mask, edit_rect 
       

#def rectbrush_grabcut(algo_data, log_data=None):
#    algo_data.mask = utils.parse_rect_brush(algo_data.mask, algo_data.position, algo_data.img_scale) 
#   # algo_data = modify_mask(algo_data, log_data)
# 
#    algo_data.mask, old_mask, edit_rect = modify_mask(algo_data, log_data)
# 
#    if log_data:
#        log_data = log_writer.main_log(algo_data, log_data, 'brushrect_before')
#        
#    if (np.sum(algo_data.mask==0)+np.sum(algo_data.mask==2) > 0) and (np.sum(algo_data.mask==1)+np.sum(algo_data.mask==3) > 0):
#        start = time.time() 
#        print "grab_cut_cv: grab cutting rectbrush"  
#        cv2.grabCut(algo_data.img,algo_data.mask,None,algo_data.bgdModel,algo_data.fgdModel,5,cv2.GC_INIT_WITH_MASK)
#        if log_data:
#            log_data = log_writer.main_log(algo_data, log_data, 'mask_grabwo')
#        
#        if not (None == old_mask):    
#            old_mask[edit_rect[0]:edit_rect[2], edit_rect[1]:edit_rect[3]] = algo_data.mask[edit_rect[0]:edit_rect[2], edit_rect[1]:edit_rect[3]]
#            algo_data.mask = copy.deepcopy(old_mask)
#            if log_data:
#                log_data = log_writer.main_log(algo_data, log_data, 'mask_grabw')
#                
#        algo_data.mask2 = np.where((algo_data.mask==2)|(algo_data.mask==0),0,1).astype('uint8')*255
#        print "grab_cut_cv: grab cut rectbrush time is", time.time()-start 
#        algo_data.flag = True               
#        
#        if log_data:
#            log_data = log_writer.main_log(algo_data, log_data, 'brushrect_after')
#    else:
#        algo_data.err_msg = ""
#        if (np.sum(algo_data.mask==0)+np.sum(algo_data.mask==2) == 0):
#            algo_data.err_msg += "please add back ground brush! "
#        if (np.sum(algo_data.mask==1)+np.sum(algo_data.mask==3) == 0):
#            algo_data.err_msg += "please add fore ground brush!"   
#        algo_data.flag = False
#        
##    ker = np.ones((10,10)) / 100.0
##    mask2 = cv2.filter2D(mask2, -1, ker)   
#    return algo_data 