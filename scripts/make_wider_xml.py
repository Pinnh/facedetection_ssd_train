import sys
import PIL
from PIL import Image
import random
import xml.etree.ElementTree as ET
from xml.dom import minidom
random.seed(42)

#min_ratio =0.035 (ref: 40/1080)
def parse_wider(text, path, train_im_path, min_face=30, min_ratio=0.031, max_blur=0, all_valid=True, 
                min_im_ratio=0.33, max_im_ratio=3.0):
    """Parse WIDER annotations from text and images
    text: text annotations
    path: path to dataset
    min_face: discard faces smaller than this
    min_ratio: discard faces with ratio face_w/max(im_w, im_h) smaller than this
    all_valid: if True, include image only if all faces are accepted
    min_im_ratio, max_im_ratio: reject images with width/height outside this range
    Returns: [(filename, width, height, numchannels, [[x1,y1,x2,y2]...])...]"""
    total_faces = 0
    total_ims = 0
    data = text.split('\n')
    data = [e for e in data if len(e)>0]
    i = 0
    res = []
    while (i<len(data)):
        file = data[i]
        im = Image.open(path+train_im_path+file)
        total_ims += 1
        check = True
        if im.bits!=8:
            print('Warning: image '+file+' data is '+str(im.bits)+'-bit, skipping')
            check = False
        if im.layers not in {3,4}:
            print('Warning: image '+file+' has '+str(im.layers)+' channels, skipping')
            check = False
        width, height = im.size
        channels = im.layers
        i+=1
        num = int(data[i])
        i+=1
        faces = []
        total_faces += num
        im_ratio = 1.0*width/height
        if (im_ratio<min_im_ratio) or (im_ratio>max_im_ratio):
            check = False
        for j in range(num):
	    if "/" in data[i]:
                continue
            face = data[i].split()
            face = [int(e) for e in face]
            x,y,w,h,blur = face[:5]
	    expression, illumination, invalid, occlusion, pose = face[5:]
            
            #if w<h:
            #    y += (h-w)//2
            #else:
            #    x += (w-h)//2

            min_wh = min(w,h)

            #cx=x+w//2
            #cy=y+w//2
            #s=max(w,h)
            #x=cx-s//2
            #y=cy-s//2
            #w=s;h=s
            x=0 if x<0 else x
            y=0 if y<0 else y
            w=width-x if w>width-x else w
            h=height-y if h>height-y else h
            
            ratio = 1.0*max(w,h)/max(width, height)
            if (min_wh>=min_face) and (ratio>=min_ratio):# and occlusion<=1:
                faces.append([x,y,x+w,y+h])
            elif all_valid:
                check = False
            i+=1
        if (len(faces)>0) and check:
            res.append((train_im_path+file, width, height, channels, faces))
    print('Total images: '+str(total_ims))
    print('Total faces: '+str(total_faces))
    return res

def write_xml_wider(data, path, xml_path, filename, write_sizes=True, shuffle=True, verbose=True):
    """Create .xml annotations and file-list for data
    data: dataset from parse_wider(...)
    path: path to dataset
    xml_path: subpath to folder for .xml
    filename: name for file-list (no extension)
    write_sizes: if True, create file with (filename, height, width) records
    shuffle: if True, shuffle lines in data
    verbose: if True, report every 1000 files"""
    img_files = [e[0] for e in data]
    xml_files = ['.'.join(e.split('.')[:-1])+'.xml' for e in img_files]
    xml_files = [xml_path + e.split('/')[-1] for e in xml_files]
    all_files = [u+' '+v for u,v in zip(img_files, xml_files)]
    
    if shuffle:
        random.shuffle(all_files)
    with open(path+filename+'.txt', 'w') as f:
        f.write('\n'.join(all_files))
        
    if write_sizes:
        sizes = [(e[0].split('/')[-1].split('.')[0], str(e[2]), str(e[1])) for e in data]
        sizes = [' '.join(e) for e in sizes]
        with open(path+filename+'_name_size.txt', 'w') as f:
            f.write('\n'.join(sizes))
     
    cnt = 0
    for item, sp in zip(data, xml_files):
        e_anno = ET.Element('annotation')
        e_size = ET.SubElement(e_anno, 'size')
        e_width = ET.SubElement(e_size, 'width')
        e_height = ET.SubElement(e_size, 'height')
        e_depth = ET.SubElement(e_size, 'depth')
        e_width.text = str(item[1])
        e_height.text = str(item[2])
        e_depth.text = str(item[3])
        for xmin,ymin,xmax,ymax in item[4]:
            e_obj = ET.SubElement(e_anno, 'object')
            e_name = ET.SubElement(e_obj, 'name')
            e_name.text = 'face'
            e_bndbox = ET.SubElement(e_obj, 'bndbox')
            e_xmin = ET.SubElement(e_bndbox, 'xmin')
            e_ymin = ET.SubElement(e_bndbox, 'ymin')
            e_xmax = ET.SubElement(e_bndbox, 'xmax')
            e_ymax = ET.SubElement(e_bndbox, 'ymax')
            e_xmin.text = str(xmin)
            e_ymin.text = str(ymin)
            e_xmax.text = str(xmax)
            e_ymax.text = str(ymax)
        txt = minidom.parseString(ET.tostring(e_anno, 'utf-8')).toprettyxml(indent='\t')
        with open(path+sp,'w') as f:
            f.write(txt)
        cnt += 1
        if (cnt%1000==0) and verbose:
            print(filename+': '+str(cnt)+' of '+str(len(data)))
 
# create labelmap for face detection           
def make_labelmap(path):
    txt = """item {
  name: "none_of_the_above"
  label: 0
  display_name: "background"
}
item {
  name: "face"
  label: 1
  display_name: "face"
}"""
    with open(path+'labelmap.prototxt', 'w') as f:
        f.write(txt)
  
if __name__ == "__main__":
    path = sys.argv[1] #dataset path
    train_xml_path = sys.argv[2] #xml subpath
    test_xml_path = sys.argv[3] #xml subpath
    
    train_im_path = "WIDER_train/images/"
    test_im_path = "WIDER_val/images/"
    
    make_labelmap(path)
    
    with open(path+'wider_face_split/wider_face_train_bbx_gt.txt') as f:
        train = f.read()
    with open(path+'wider_face_split/wider_face_val_bbx_gt.txt') as f:
        test = f.read()
    
    print('Parsing WIDER dataset...')
    
    print('Train:')
    train = parse_wider(train, path, train_im_path)
    print('Accepted images: '+str(len(train)))
    print('Accepted faces: '+str(sum([len(e[4]) for e in train])))    
    
    print('Test:')
    test = parse_wider(test, path, test_im_path)
    print('Accepted images: '+str(len(test)))
    print('Accepted faces: '+str(sum([len(e[4]) for e in test])))
    
    print('Creating .xml annotations and file lists...')
    
    print('Train:')
    write_xml_wider(train, path, train_xml_path, 'trainval', write_sizes=False)
    print('Test:')
    write_xml_wider(test, path, test_xml_path, 'test', shuffle=False)
    
    print('Done')
