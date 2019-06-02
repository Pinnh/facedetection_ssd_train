import os, sys
import cv2
import numpy as np
sys.path.insert(0,"/media/pinnacle/ext1/workspace/caffe/build/install/python")
import caffe

import matplotlib.pylab as plt

def transform_input(img, transpose=True, dtype=np.float32):
    """Return transformed input image 'img' for CNN input
    transpose: if True, channels in dim 0, else channels in dim 2
    dtype: type of returned array (sometimes important)    
    """
    inpt = cv2.resize(img, (640,480))
    inpt = inpt - 127.5
    inpt = inpt / 127.5
    inpt = inpt.astype(dtype)
    if transpose:
        inpt = inpt.transpose((2, 0, 1))
    return inpt
    
def transform_output(img, output):
    """Extract bbox info from NN output
    img: original image
    output: NN output
    returns: boxes(list of array[4]), classes(list of int), confidence(list of float)"""
    h,w = img.shape[:2] 
    boxes = (output['detection_out'][0,0,:,3:7] * np.array([w, h, w, h])).astype(int)
    classes = output['detection_out'][0,0,:,1].astype(int)
    confidence = output['detection_out'][0,0,:,2]
    if (len(confidence)==1) and (confidence[0]<0):
        return [],[],[]
    return boxes, classes, confidence

if __name__ == "__main__":
    # Test Net on several images from images/input, draw bboxes, save to images/output
    path = sys.argv[3] 
    save_path = 'images/output/'
    proto = sys.argv[1]    
    weight= sys.argv[2]
    
    net = caffe.Net(proto, weight, caffe.TEST)
    
    print('OK')
    
    images = os.listdir(path)
    
    for p in images:
        im = cv2.imread(path+p)
        inpt = transform_input(im)
        net.blobs['data'].data[...] = inpt
        output = net.forward() 
        boxes, classes, confidence = transform_output(im, output)
        for box, cls, conf in zip(boxes, classes, confidence):
            col = float(conf)
            print("conf:",conf)
            col = (col*np.array([0,0,255]) + (1-col)*np.array([0,0,255])).astype(int)
            col = [int(c) for c in col]
            cv2.rectangle(im, (box[0], box[1]), (box[2], box[3]), col, 3)

	plt.imshow(cv2.cvtColor(im,cv2.COLOR_RGB2BGR))

	plt.show()
        
