'''
' ==============================================================
' Download bundle to current computer (next step is git submit)
' --------------------------------------------------------------
' This script needs: gg-plangrid-build-mobile-bundle-check.bas
' --------------------------------------------------------------
' Version 1.1
' 2022-04-11
' add inline pattern check
' --------------------------------------------------------------
' Version 1.0
' 2022-02-18
' add gg-plangrid-build-mobile target length check
' Script will stop is target length over limitation
' --------------------------------------------------------------
' Welocalize Jinan
' ==============================================================
'''

import json
import sys
import os
import shutil
import re
import subprocess
try:
    from openpyxl import load_workbook
except:
    print("install openpyxl: 'pip install openpyxl', try again please.")
    sys.exit()
    

def findLatestBundleNum(bunle_normal_path):
    for i in range(6,0,-1):
        if os.path.isdir(bunle_normal_path+"_"+str(i)):
            return str(i)
    return False


def getBeiExabloxPath(project_name):
    s_file = open("bundleConf.json",encoding='utf-8')
    data = json.load(s_file)
    s_file.close()
    for gg_item in data["gg"]:
        if( gg_item == project_name ):
            return "gg"
            break
    for bim_item in data["bim"]:
        if( bim_item == project_name ):
            return "bim"
            break
    for bim_item in data["bc"]:
        if( bim_item == project_name ):
            return "bc"
            break
    return False
    
def get_files_in_dir(root_dir):
    list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            list.append(os.path.join(dirpath, filename))
    return list

def getBundleList():
    s_file = open("bundle.txt",encoding='utf-8')
    file_content = s_file.read()
    s_file.close()
    file_content = re.sub("\n+$","",file_content)
    bundle_list = file_content.split("\n")
    for i in range(len(bundle_list)):
        bundle_list[i] = bundle_list[i].strip()
        if bundle_list[i] == "Bim360reports-ui":
            bundle_list[i] = "BIM360reports-ui"
    return bundle_list
    
def find_repos():
    files = os.listdir('.')
    return [file for file in files if file.endswith('_repos.xlsx')]
    
def xlsx_data():
    repos = find_repos()
    latest_repos = repos[-1]
    # print("latest_repos:",latest_repos)
    data = []
    wb = load_workbook(latest_repos)
    ws = wb.active
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:
            continue
        # print(row[0])
        data.append(row)
    return data
    
def getRepoLang(repoName):
    xlsx_list = xlsx_data()
    for xlsx_row in xlsx_list:
        if xlsx_row[0] == repoName:
            return xlsx_row[2].upper().split(",")
            break
    return False
    
def is_bundle_file(filename):
    return re.match(r'.*\.tbulic[0-9]{2}$', filename, re.I) is not None
    
def main(bundle_date):
    bundle_list = getBundleList()
    #check bundle exist or not
    for bundle_item in bundle_list:
        upload_path = r"S:\Favorites\BIM-ACC\Bundle_Transfer\FromTrans\{}\{}".format(bundle_item,bundle_date)
        if(os.path.isdir(upload_path) == False):
            if findLatestBundleNum(upload_path) == False:
                print("bundle not exist on: "+bundle_item)
                print("check path is: "+upload_path)
                sys.exit()
        local_path = bundle_item+"\\lpu\\All\\.BundleTransfer\\FromTrans\\"+bundle_date
        if(os.path.isdir(local_path) == True):
            print("bundle already exist on local PC: "+bundle_item)
            sys.exit()
    #compare the bundle number with releaseToDev number
    for bundle_item in bundle_list:
        upload_path = r"S:\Favorites\BIM-ACC\Bundle_Transfer\FromTrans\{}\{}".format(bundle_item,bundle_date)
        if os.path.isdir(upload_path) == False:
            bundle_num = findLatestBundleNum(upload_path)
            upload_path = upload_path + "_" + bundle_num
        conf_lang = getRepoLang(bundle_item)
        if conf_lang == False:
            print("conf_lang error:",bundle_item)
            sys.exit()
        conf_lang.sort()
        from_lang = os.listdir(upload_path)
        from_lang.sort()
        if conf_lang != from_lang:
            print("back lang not same with conf lang")
            print("back lang: ".ljust(18, " ")+ str(from_lang) )
            print("conf lang: ".ljust(18, " ")+ str(conf_lang) )
            print("upload_path: "+upload_path)
            sys.exit()
    #start copy bundle
    for bundle_item in bundle_list:
        upload_path = r"S:\Favorites\BIM-ACC\Bundle_Transfer\FromTrans\{}\{}".format(bundle_item,bundle_date)
        print("downloading on: "+bundle_item)
        local_path = bundle_item+"\\lpu\\All\\.BundleTransfer\\FromTrans\\"+bundle_date
        if os.path.isdir(upload_path) == False:
            bundle_num = findLatestBundleNum(upload_path)
            upload_path = upload_path + "_" + bundle_num
            local_path = local_path + "_" + bundle_num
            print("upload_path:",upload_path)
            print("local_path:",local_path)
        shutil.copytree(upload_path,local_path)
        #check there only .tbulic22 files, otherwise ask whether delete it
        print("[checking bundles]")
        files = get_files_in_dir(local_path)
        for file in files:
            if is_bundle_file(file) == False:
                print(file)
                del_input = input("This file is not bundle, delete it? [enter or n]:\n")
                if del_input == "n":
                    pass
                else:
                    # os.remove(file)
                    os.system('del /f "{}"'.format(file))
    #check langs, if bundle was remove by script, copy them from ToTrans to FromTrans
    print("[info]compare ToTrans and FromTrans")
    for bundle_item in bundle_list:
        local_from_path = bundle_item+"\\lpu\\All\\.BundleTransfer\\FromTrans\\"+bundle_date
        local_to_path   = bundle_item+"\\lpu\\All\\.BundleTransfer\\ToTrans\\"+bundle_date
        if os.path.isdir(local_from_path) == False:
            bundle_num = findLatestBundleNum(local_from_path)
            local_from_path = local_from_path + "_" + bundle_num
            local_to_path = local_to_path + "_" + bundle_num
        from_langs = os.listdir(local_from_path)
        to_langs = os.listdir(local_to_path)
        for to_lang in to_langs:
            if to_lang not in from_langs:
                print("copy: ",local_to_path + "\\" + to_lang)
                # print(local_from_path + "\\" + to_lang + "\\" + bundle_item + "__" + to_lang.lower() + "_Statistics.txt")
                shutil.copytree(local_to_path + "\\" + to_lang, local_from_path + "\\" + to_lang)
                os.remove( local_from_path + "\\" + to_lang + "\\" + bundle_item + "__" + to_lang.lower() + "_Statistics.txt" )
        
    print("[info]download finished")
    if "ACS-BuildingConnected-BC" in bundle_list or "ACS-BuildingConnected-client" in bundle_list:
        print("Don't forget leverage eng to enn for BC!")
        

def checkInput(bundle_date):
    date_confirm = input("Bundle date confirm: "+bundle_date+" [y or n or input date]:\n")
    if date_confirm == "n":
        print("script stoped")
        sys.exit()
    elif date_confirm == "y" or date_confirm == "":
        print("start download bundle date: "+bundle_date)
        main(bundle_date)
    elif re.match("\d{4}-\d{2}-\d{2}",date_confirm) != None:
        checkInput(date_confirm)
    else:
        print("input error, retry please")
        date_confirm = input("Input bundle date please: [input date]:\n")
        checkInput(date_confirm)
        
date_confirm = input("Input bundle date please: [input date]:\n")
checkInput(date_confirm)
# checkInput("2022-04-11")
# print(xlsx_data())
# print(xlsx_data()[0][0])