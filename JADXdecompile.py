from Common import *
import subprocess
import os

def decompile_apk(apk_path):

    try:
        # Check if output directory exists, create it if it doesn't
        if not os.path.exists(JADXPATH):
            os.makedirs(JADXPATH)
        
        # Run the jadx command to decompile the APK
        subprocess.run(['jadx', '-d', JADXPATH + "/" + apk_path.split('/')[-1][:-4], apk_path])
        
        print(f"Decompiled code has been saved in {JADXPATH}")
    
    except Exception as e:
        print(f"An error occurred: {e}")