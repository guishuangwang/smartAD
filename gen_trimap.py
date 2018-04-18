#! /usr/bin/python
# -*- coding: utf-8 -*- #
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def gen_trimap(mask, r = 0.01):
    '''
    generate trimap from segmentation, 
    input:
    mask 0 for bg 1 for fg
    output:
    0, bg
    255, fg
    128, uncertain
    '''
    mask = (mask > 0.5).astype(np.int16)*255
    h, w = mask.shape[:2]
    delta = int(min(h, w) * r) + 3;
    border = get_border(mask);
    kernel = np.ones((delta, delta), np.uint8)
    uncertain = cv2.dilate(border, kernel, iterations=1)
    mask[uncertain > 0] = 128
    return mask.astype(np.uint8)

def get_border(im):
    ddepth = cv2.CV_16S
    dx = cv2.Sobel(im, ddepth, 1, 0)
    dy = cv2.Sobel(im, ddepth, 0, 1)
    dxabs = cv2.convertScaleAbs(dx)
    dyabs = cv2.convertScaleAbs(dy)
    mag = cv2.addWeighted(dxabs, 1, dyabs, 1, 0)
    border = (mag > 0).astype(np.uint8);
    return border

if __name__ == "__main__":
    x = cv2.imread("images/try_mask.png", 0)
    x = (x > 0).astype(np.int16)
    y = get_border(x)
    z = gen_trimap(x)
    cv2.imshow("y", y*255);
    cv2.imshow("z", z);
    cv2.waitKey(0)
