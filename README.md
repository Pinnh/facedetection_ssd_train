# SSDFaceTrain
 Caffe SSD Face Detector Training Script

## Requires

 Caffe-SSD: you need install **caffe-ssd** first, caffe-ssd you can find at [[here]](https://github.com/weiliu89/caffe))
 Wider Face Dataset: 
 
 ## Train
 
 Before you start training, you need to modify some codes in Makefile
 
 Make wider face lmdb data
 ```
 make wider_lmdb
 ```
 Train
 ```
 make train
 ```
 
 ## Result
