cur_dir := "$(shell pwd)"
wider_name :=WIDERfacedet
fddb_name :=FDDBfacedet
combine_name :=WIDER_facedet
data_dir := /media/pinnacle/ext1/data/face/WIDER 
wider_dir := /media/pinnacle/ext1/data/face/WIDER/WIDERfacedet
fddb_dir := $(data_dir)/$(fddb_name)

lmdb_pyscript := /media/pinnacle/ext1/workspace/caffe/scripts/create_annoset.py
caffe_exec := /media/pinnacle/ext1/workspace/caffe/build/tools/caffe

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
# FDDB
fddb_xml:
	cd $(fddb_dir) && \
	mkdir -p -v xml && \
	cd xml && \
	mkdir -p -v trainval && \
	mkdir -p -v test && \
	cd $(cur_dir) && \
	python ./scripts/make_fddb_xml.py $(fddb_dir)/ xml/trainval/ xml/test/
fddb_lmdb: fddb_xml
	python $(lmdb_pyscript) --anno-type=detection --label-map-file=$(fddb_dir)/labelmap.prototxt \
	--min-dim=0 --max-dim=0 --resize-width=0 --resize-height=0 --check-label --encode-type=jpg --encoded \
	--redo \
	$(fddb_dir) $(fddb_dir)/trainval.txt $(fddb_dir)/lmdb/fddb_train_lmdb \
	./data; \
	python $(lmdb_pyscript) --anno-type=detection --label-map-file=$(fddb_dir)/labelmap.prototxt \
	--min-dim=0 --max-dim=0 --resize-width=0 --resize-height=0 --check-label --encode-type=jpg --encoded \
	--redo \
	$(fddb_dir) $(fddb_dir)/test.txt $(fddb_dir)/lmdb/fddb_test_lmdb \
	./data \

# WIDER and FDDB
merge_datasets: 
	cd $(data_dir) && \
	mkdir -p -v $(combine_name) && \
	cd $(cur_dir) && \
	python ./scripts/merge_wider_fddb.py $(data_dir)/ $(wider_name)/ $(fddb_name)/ $(combine_name)/

lmdb: wider_xml fddb_xml merge_datasets
	python $(lmdb_pyscript) --anno-type=detection --label-map-file=$(data_dir)/$(combine_name)/labelmap.prototxt \
	--min-dim=0 --max-dim=0 --resize-width=0 --resize-height=0 --check-label --encode-type=jpg --encoded \
	--redo \
	$(data_dir) $(data_dir)/$(combine_name)/trainval.txt \
	$(data_dir)/$(combine_name)/lmdb/wider_fddb_train_lmdb \
	./data; \
	python $(lmdb_pyscript) --anno-type=detection --label-map-file=$(data_dir)/$(combine_name)/labelmap.prototxt \
	--min-dim=0 --max-dim=0 --resize-width=0 --resize-height=0 --check-label --encode-type=jpg --encoded \
	--redo \
	$(data_dir) $(data_dir)/$(combine_name)/test.txt \
	$(data_dir)/$(combine_name)/lmdb/wider_fddb_test_lmdb \
	./data \

# TRAIN -weights model/yufacedetectnet-open-v1.caffemodel
train:
	$(caffe_exec) train -solver solver_train.prototxt -weights model/snapshot/ssdfacedet_iter_3500.caffemodel 2>&1 | \
	tee `cat solver_train.prototxt | grep snapshot_prefix | grep -o \".* | tr -d \"`_log.txt
resume:
	$(caffe_exec) train -solver solver_train.prototxt -snapshot `cat snapshot.txt` 2>&1 | \
	tee -a `cat solver_train.prototxt | grep snapshot_prefix | grep -o \".* | tr -d \"`_log.txt
