import json
import sys
import os
import shutil
import re
import subprocess

#confirm validate languages, format: 3 lowcase character language code in list
#this line always needs open
# LANGS   =   ["csy","plk","ptb"]
LANGS   =   ["csy","hun","fin","ptb"]
#LANGS   =   ["csy"]
#LANGS   =   ["hun"]
#LANGS   =   ["csy","plk"]
# LANGS   =   ["csy"]
#LANGS   =   ["plk"]

try:
    LANGS
except NameError:
    LANGS = None
    
if LANGS != None:
    confirm_msg = input("Confirm langs: "+str(LANGS)+", pls type [y or n]:\n")
    if confirm_msg == "n":
        print("script stoped")
        sys.exit()

def getBundleList():
    s_file = open("repos.txt",encoding='utf-8')
    file_content = s_file.read()
    s_file.close()
    file_content = re.sub("\n+$","",file_content)
    bundle_list = file_content.split("\n")
    for i in range(len(bundle_list)):
        bundle_list[i] = bundle_list[i].strip()
    return bundle_list
    
def findLatestBundleNum(bunle_normal_path):
    for i in range(4,0,-1):
        if os.path.isdir(bunle_normal_path+"_"+str(i)):
            return str(i)
    return False

def main(bundle_date):
    bundle_list = getBundleList()
    #check repo name
    for dir_item in bundle_list:
        if os.path.isdir(dir_item) == False:
            print("repo name error: ",dir_item)
            sys.exit()
    #check bundle all exist
    for bundle_item in bundle_list:
        # if bundle_item not in ["acc-handover"]:
            # continue
        bundle_path = bundle_item + "\\lpu\All\\.BundleTransfer\\FromTrans\\" + bundle_date
        if os.path.isdir(bundle_path) == False:
            bundle_num = findLatestBundleNum(bundle_path)
            if bundle_num == False:
                print("bundle not exist on: "+bundle_path)
                sys.exit()
            bundle_path = bundle_path + "_" + bundle_num
        if os.path.isdir(bundle_path) == False:
            print("bundle not exist on: "+bundle_path)
            sys.exit()
    validate_error = []
    for bundle_item in bundle_list:
        # if bundle_item not in ["acc-handover"]:
            # continue
        bundle_path = bundle_item + "\\lpu\All\\.BundleTransfer\\FromTrans\\" + bundle_date
        if os.path.isdir(bundle_path) == False:
            bundle_num = findLatestBundleNum(bundle_path)
            bundle_path = bundle_path + "_" + bundle_num
            
        for file in os.listdir(bundle_path):
            d = os.path.join(bundle_path, file)
            bundle_file = d + "\\" + bundle_item + ".tbulic22"
            cur_lang = bundle_file.split("\\")[-2]
            if LANGS != None and cur_lang.lower() not in LANGS:
                continue
            # if cur_lang.lower() not in ["plk"]:
                # continue
            # print(bundle_file)
            print("validate: ",bundle_file)
            result = subprocess.run(["C:/Program Files (x86)/Trados/Passolo/Passolo 2022/pslcmd.exe", "/openproject:"+bundle_file,"/runmacro=bimComment.bas"], stdout=subprocess.PIPE,text=True)
            check_result = result.stdout
            temp_list = []
            temp_list.append(check_result)
            # print(temp_list)
            check_result_list = check_result.split("\n")
            if check_result_list[-1] == "":
                check_result_list.pop()
            # print(check_result_list)
            # print(check_result_list[-1])
            # print(check_result_list[-2])
            # print(check_result_list[-1]!= "Total invalidate number(red): 0")
            # print(check_result_list[-2]!= "Total comment check number(blue green): 0")
            if check_result_list[-1] != "Total invalidate number(red): 0" or check_result_list[-2] != "Total invalidate number(blue green): 0":
                validate_error.append({bundle_item:check_result_list})
    if len(validate_error) > 0:
        print("validate error happen:")
        for error_item in validate_error:
            for k,v in error_item.items():
                print(k)
                for error_v in v:
                    print("\t",error_v)
    if len(validate_error) == 0:
        print("validate language looks good!")

def checkInput(bundle_date):
    date_confirm = input("Bundle date confirm: "+bundle_date+" [y or n or input date]:\n")
    if date_confirm == "n":
        print("script stoped")
        sys.exit()
    elif date_confirm == "y" or date_confirm == "":
        print("start validate lang bundle date: "+bundle_date)
        main(bundle_date)
    elif re.match("\d{4}-\d{2}-\d{2}",date_confirm) != None:
        checkInput(date_confirm)
    else:
        print("input error, retry please")
        date_confirm = input("Input bundle date please: [input date]:\n")
        checkInput(date_confirm)
        
date_confirm = input("Input bundle date please: [input date]:\n")
checkInput(date_confirm)
# checkInput("2022-07-15")