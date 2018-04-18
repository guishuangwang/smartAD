#! /usr/bin/python
# -*- coding: utf-8 -*- #
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import gen_trimap
import guidedfilter
import knn_matting

def matte(img, seg, method="guided"):
    '''
    img 3 channel uint8 value 0-255
    seg 1 channel float value 0,1
    output alpha 1 channel float value 0-1
    '''
    if "guided" == method:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = gray.astype(np.float64) / 255.0
        alpha = guidedfilter.guidedfilter(gray, seg, 3, 0.0001)
    elif "knn" == method:
        trimap = gen_trimap.gen_trimap(seg)
        alpha = knn_matting.knn_matte(img, trimap)
    else:
        return seg
    alpha[alpha < 0] = 0
    alpha[alpha > 1] = 1
    return alpha

if __name__ == '__main__':
    #method = "guided"
    method = "knn"
    img = cv2.imread("images/img.jpg")
    seg = cv2.imread("images/mask.png", 0).astype(np.float64)
    alpha = matte(img, seg, method)
    cv2.imshow("img", img)
    cv2.imshow("seg", seg)
    cv2.imshow("alpha", alpha)
    cv2.waitKey(0)
