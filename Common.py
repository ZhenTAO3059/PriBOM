#!/usr/bin/env python3
import sys
import csv
csv.field_size_limit(2**31 - 1)
import os
import hashlib

CLIENT = "GUIHierarchyPrinterClient"
ANDROID_SDK = "/mnt/d/Softwares/Android/Sdk" # change to your Android Sdk directory
XMLPATH = "./XMLOutput"
APKPATH = "./APK"
CSVPATH = "./XML2CSV"
JADXPATH = "./XMLOutput"
InfoSet = "./InfoSet"
DEFAULT_MAX_JOB = 15
MAPPINGPATH = "./Mapping"


def getFileList(rootDir, pickstr):
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pickstr in filename:
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


def check_and_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()
