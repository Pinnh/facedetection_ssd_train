cur_dir := "$(shell pwd)"
wider_name :=WIDERfacedet

wider_dir := /media/pinnacle/ext1/data/face/WIDER

caffe_dir := /media/pinnacle/ext1/workspace/caffe
lmdb_pyscript := $(caffe_dir)/scripts/create_annoset.py
caffe_exec := $(caffe_dir)/build/tools/caffe

# WIDER
wider_xml:
	cd $(wider_dir) && \
	cd WIDER_train && \
	mkdir -p -v xml && \
	cd ../WIDER_val && \
	mkdir -p -v xml && \
	cd $(cur_dir) && \
	python ./scripts/make_wider_xml.py $(wider_dir)/ WIDER_train/xml/ WIDER_val/xml/
	
wider_lmdb: wider_xml
	python $(lmdb_pyscript) --anno-type=detection --label-map-file=$(wider_dir)/labelmap.prototxt \
	--min-dim=0 --max-dim=0 --resize-width=0 --resize-height=0 --check-label --encode-type=jpg --encoded \
	--redo \
	$(wider_dir) $(wider_dir)/trainval.txt $(wider_dir)/WIDER_train/lmdb/wider_train_lmdb \
	./data; \
	python $(lmdb_pyscript) --anno-type=detection --label-map-file=$(wider_dir)/labelmap.prototxt \
	--min-dim=0 --max-dim=0 --resize-width=0 --resize-height=0 --check-label --encode-type=jpg --encoded \
	--redo \
	$(wider_dir) $(wider_dir)/test.txt $(wider_dir)/WIDER_val/lmdb/wider_test_lmdb \
	./data \

# TRAIN -weights model/yufacedetectnet-open-v1.caffemodel
train:
	$(caffe_exec) train -solver solver_train.prototxt -weights model/snapshot/ssdfacedet_iter_3500.caffemodel 2>&1 | \
	tee `cat solver_train.prototxt | grep snapshot_prefix | grep -o \".* | tr -d \"`_log.txt
resume:
	$(caffe_exec) train -solver solver_train.prototxt -snapshot `cat snapshot.txt` 2>&1 | \
	tee -a `cat solver_train.prototxt | grep snapshot_prefix | grep -o \".* | tr -d \"`_log.txt
