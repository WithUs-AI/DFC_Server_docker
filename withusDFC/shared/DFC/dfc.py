# importing everything needed
#%matplotlib inline

import os
import json
import numpy as np
import tensorflow as tf
import pandas as pd
import matplotlib.patches as patches
import DB_control
import pdb

from IPython.display import SVG
from IPython.display import display
from matplotlib import pyplot as plt
from PIL import Image
from hailo_sdk_client import ClientRunner, InferenceContext
from tensorflow.python.eager.context import eager_mode

dfc_db = DB_control.DFC_DB('192.168.30.121','zaiv','hello','Zaiv')

# colab에서 할 일
def preproc(image, output_height=640, output_width=640, resize_side=640):
    ''' imagenet-standard: aspect-preserving resize to 256px smaller-side, then central-crop to 224px'''
    with eager_mode():
        h, w = image.shape[0], image.shape[1]
        scale = tf.cond(tf.less(h, w), lambda: resize_side / h, lambda: resize_side / w)
        resized_image = tf.compat.v1.image.resize_bilinear(tf.expand_dims(image, 0), [int(h*scale), int(w*scale)])
        cropped_image = tf.compat.v1.image.resize_with_crop_or_pad(resized_image, output_height, output_width)
        return tf.squeeze(cropped_image)

# onnx file check
def onnxCheck(rootdir) :
    onnxEx= '.onnx'
    onnx_list = [file for file in os.listdir(rootdir) if file.endswith(onnxEx)]
    
    print(onnx_list)
    
    if len(onnx_list) == 1 :
        return onnx_list[0]
    else :
        print("Onnx파일이 없거나 여러개 있습니다. 컴파일할 Onnx 파일 하나만 남겨주세요.")
        return ""
    
# json file check
def jsonCheck(rootdir) :
    jsonEx= '.json'
    json_list = [file for file in os.listdir(rootdir) if file.endswith(jsonEx)]
    
    print(json_list)
    
    if len(json_list) == 1 :
        return json_list[0]
    else :
        print("json파일이 없거나 여러개 있습니다. nms_config 파일 하나만 남겨주세요.")
        return ""
    
# npy file check
def npyCheck(rootdir) :
    npyEx= '.npy'
    npy_list = [file for file in os.listdir(rootdir) if file.endswith(npyEx)]
    
    print(npy_list)
    
    if len(npy_list) == 1 :
        return npy_list[0]
    else :
        print("npy파일이 없거나 여러개 있습니다. 사용할 데이터셋 하나만 남겨주세요.")
        return ""

def SetVariable(dfcdata):
    global yolo_model_name
    global parse_har_name
    global quantized_har_name
    global compile_har_name
    global hef_name
    global yolo_onnx_model_path
    global nms_json_path
    global cal_images_path
    global alls_file_path
    global token
    
    token = dfcdata[0]
    rootpath = dfcdata[1]
    workpath = rootpath + "/" + token
    
    print(type(dfcdata))
    print(dfcdata)
    print(token)
    print(workpath)
    
    yolo_model_name = '{0}_Model'.format(token)
    yolo_onnx_model_path = '{0}/{1}'.format(workpath,onnxCheck(workpath))
    parse_har_name= '{0}/har/{1}_parse.har'.format(workpath,yolo_model_name)
    quantized_har_name = '{0}/har/{1}_quantized.har'.format(workpath,yolo_model_name)
    compile_har_name = '{0}/har/{1}_compiled_model.har'.format(workpath,yolo_model_name)
    hef_name = '{0}/hef/{1}.hef'.format(workpath,yolo_model_name)
    svg_check = '{0}/svg/{1}.svg'.format(workpath,yolo_model_name)
    nms_json_path = '{0}/{1}'.format(workpath,jsonCheck(workpath))
    cal_images_path = '{0}/dataset/{1}'.format(workpath,npyCheck(workpath+'/dataset/'))
    alls_file_path = rootpath + '/Alls/'
    
    print(yolo_model_name)
    print(yolo_onnx_model_path)
    print(parse_har_name)
    print(quantized_har_name)
    print(compile_har_name)
    print(nms_json_path)
    print(hef_name)
    print(cal_images_path)
    print(alls_file_path)

def Make_alls(def_alls, data_len):
    # Load the model script to ClientRunner so it will be considered on optimization
    allsfile = alls_file_path+def_alls
    resultfile = alls_file_path+yolo_model_name+".alls"

    new_text_content = ''
    target_word1 = '<jsonpath>'
    target_word2 = '<calsize>'

    new_word1 = nms_json_path
    new_word2 = str(data_len)

    with open(allsfile,'r') as f:
        lines = f.readlines() ## 기존 텍스트파일에 대한 내용을 모두 읽는다.
        for i, l in enumerate(lines):
            new_string = l.strip().replace(target_word1,new_word1)
            new_string = new_string.strip().replace(target_word2,new_word2)
            
            print(new_string)
            if new_string:
                new_text_content += new_string + '\n'
            else:
                new_text_content += '\n'
                
    with open(resultfile,'w') as f:
        f.write(new_text_content)

    print(resultfile)
    return resultfile

def DFC_run() :
    try:
        Modeldata = dfc_db.Get_Model(token)
        print(Modeldata)

        if Modeldata[0]=='onnx' :
            runner = ClientRunner(hw_arch=Modeldata[1])
            hn, npz = runner.translate_onnx_model(yolo_onnx_model_path, yolo_model_name, 
                                            start_node_names=['images'], 
                                            end_node_names=["/model.24/m.0/Conv","/model.24/m.1/Conv","/model.24/m.2/Conv"], 
                                            net_input_shapes={'images':[1, 3, Modeldata[2], Modeldata[2]]})

        runner.save_har(parse_har_name)

        #SVG('animal_model.svg')

        #src = 'animal_model.svg'
        #dist = 'withus/svg/animal_model_paser.svg'
        #shutil.move(src,dist)

        calib_dataset = np.load(file=cal_images_path)
        
        resultfile = Make_alls(Modeldata[3],len(calib_dataset))
        
        runner.load_model_script(resultfile)
        runner.optimize(calib_dataset)

        runner.save_har(quantized_har_name)

        hef = runner.compile()

        with open(hef_name, 'wb') as f:
            f.write(hef)

        runner.save_har(compile_har_name)
        return "pass"
    except Exception as e :
        print(e)
        return "fail"

def main():
    print("python main function")
    
    try:
        while True:
            item = dfc_db.Get_uploaded()
            
            if item!=0 and len(item) > 0 :
                print("find data")
                SetVariable(item)
                print("Dir Set End")
                dfc_db.Set_start(token)
                print("state change")
                print("dfc_run start")
                result = DFC_run()
                if result == "fail" :
                    print("DFC_ERROR!!!")
                    dfc_db.Set_Error(token)
                else :
                    print("DFC_end!")
                    dfc_db.Set_finish(os.path.basename(hef_name),token)
                    print("state change")
                    print("end!")
                
    except (RuntimeError, TypeError) as a:
        print(a)
        dfc_db.Close_db()

if __name__ == '__main__':
    main()
