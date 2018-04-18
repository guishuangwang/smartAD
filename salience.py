import tensorflow as tf
import numpy as np
import os
from scipy import misc
import argparse
import sys
import cv2
import copy
import log_writer
import imutils 
import pickle

#import dss_infer
#import crf

gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction = 0.5)
def rgba2rgb(img):
    return img[:,:,:3]*np.expand_dims(img[:,:,3],2)


def salience_matting(rgb): # rgb is image input
    origin_shape = rgb.shape[:2]
    g_mean = np.array(([126.88,120.24,112.19])).reshape([1,1,3])
    with tf.Session() as sess:
      	saver = tf.train.import_meta_graph('./meta_graph/my-model.meta')
      	saver.restore(sess,tf.train.latest_checkpoint('./salience_model'))
      	image_batch = tf.get_collection('image_batch')[0]
      	pred_mattes = tf.get_collection('mask')[0]
   
        rgb = np.expand_dims(misc.imresize(rgb.astype(np.uint8),[320,320,3],interp="nearest").astype(np.float32)-g_mean,0)
    
        feed_dict = {image_batch:rgb}
        pred_alpha = sess.run(pred_mattes,feed_dict = feed_dict)
        mask =  misc.imresize(np.squeeze(pred_alpha), origin_shape)
 
        return mask
'''
def SOD_main(algo_data, log_data): 
    log_data = log_writer.main_log(algo_data, log_data, 'init')
    
    rgb = algo_data.img
    if rgb.shape[2]==4:
        rgb = rgba2rgb(rgb)
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction = 0.2)
    algo_data.mask = salience_matting(rgb, gpu_options)
    algo_data.mask2 = copy.deepcopy(algo_data.mask)

    log_data = log_writer.main_log(algo_data, log_data, 'mask2')

    algo_data.flag = True
    return algo_data
'''

def init_salience_model():
    model_files = ['deploy.prototxt', 'dss_model_released.caffemodel']
    net = dss_infer.init_model(model_files)
    return net
'''
def salience_matting(rgb, net): # rgb is image input
    origin_shape = rgb.shape[:2]
    small_shape = origin_shape[:]
    # narrow alpha size
    rf = False
    if max(origin_shape) > 512.0: #NOTE! need to back change to 512.0
        ratio = 512.0 / max(origin_shape)#NOTE!  need to back change to 512.0
        rgbs = cv2.resize(rgb, (0,0), fx = ratio, fy = ratio, interpolation = cv2.INTER_NEAREST)
        small_shape = rgbs.shape[:2]
        rf = True

    if rf:
        alpha = dss_infer.predict(rgbs, net)
    else:
        alpha = dss_infer.predict(rgb, net)
    mask =  misc.imresize(np.squeeze(alpha), small_shape)

    if rf:
        #mask = cv2.resize(mask, origin_shape, cv2.INTER_CUBIC)
        mask =  misc.imresize(mask, origin_shape)

    # dense crf
    #mask = crf.sal_dcrf(rgb, mask)

    return mask
'''
def SOD_main(algo_data, log_data): 
    log_data = log_writer.main_log(algo_data, log_data, 'init')
    
    rgb = algo_data.img
    if rgb.shape[2]==4:
        rgb = rgba2rgb(rgb)
    #net = init_salience_model()
    #algo_data.mask = salience_matting(rgb, net)
    algo_data.mask = salience_matting(rgb)
    
    
    #with open('images/tmp.pkl', 'w') as f:
    #    pickle.dump(algo_data.mask, f)
    
    #with open('images/tmp.pkl') as f:
    #    algo_data.mask = pickle.load(f)
        
    algo_data.mask2 = copy.deepcopy(algo_data.mask)
    
    sub_masks, sub_rects = seperate_mask(algo_data.mask)
    algo_data.sub_masks = [{'mask': sub_masks[s], 'rect': sub_rects[s]} for s in xrange(len(sub_masks))]
    
    log_data = log_writer.main_log(algo_data, log_data, 'mask2')
     
    
    algo_data.flag = True
    return algo_data

def seperate_mask(mask):
    sub_masks, sub_rects = [], []
    
    mask2 = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)[1]
    print type(mask2)
    print mask2.shape
    all_pixel = mask2.shape[0] * mask2.shape[1]
    N_kernel = 2*max(1, int(np.sqrt(all_pixel) * 0.01))+1
    kernel=np.uint8(np.zeros((N_kernel, N_kernel)))  
    for k in range(N_kernel):  
        kernel[k, (N_kernel-1)/2]=1  
        kernel[(N_kernel-1)/2, k]=1  
        
    mask2=cv2.erode(mask2, kernel);  
    h, w = mask2.shape[0], mask2.shape[1]
    
    cnts = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    
    for n_iter, points in enumerate(cnts):
        if points.shape[0] < 10:
            continue    
        tmp_mask = np.zeros(mask2.shape)
        rect = [np.min(points[:, 0, 1]), np.min(points[:, 0, 0]), np.max(points[:, 0, 1]), np.max(points[:, 0, 0])]
        rect[0], rect[1] = max(0, int(rect[0]-N_kernel*0.6)), max(0, int(rect[1]-N_kernel*0.6))
        rect[2], rect[3] = min(h, int(rect[2]+N_kernel*0.6)), min(w, int(rect[3]+N_kernel*0.6))
        print rect
        print tmp_mask.shape
        print mask.shape
        tmp_mask[rect[0]:rect[2], rect[1]:rect[3]] = mask[rect[0]:rect[2], rect[1]:rect[3]]
        sub_masks.append(copy.deepcopy(tmp_mask))
        sub_rects.append(copy.deepcopy(rect))
           
    return sub_masks, sub_rects
    
    
 
    
    
   


if __name__ == "__main__":
    rgb = cv2.imread(sys.argv[1])
    net = init_salience_model()
    mask = salience_matting(rgb, net)
    print mask
    cv2.imshow("mask", mask)
    cv2.waitKey(0)
