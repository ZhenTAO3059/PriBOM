#!/usr/bin/env python3
import re
import subprocess
import threadpool
from Common import *

class GatorCaller:
    def call_gator(self, apk):
        apk_name = os.path.split(apk)[-1][:-4]
        print("[+] Analysing " + apk_name)
        new_gator_file = os.path.join(XMLPATH, apk_name + ".xml")
        if os.path.exists(new_gator_file):
            return

        try:
            CMD = "./gator-3.8/gator/gator a --sdk " + ANDROID_SDK + " -p \"" + apk + "\" -client " + CLIENT
            out_bytes = subprocess.check_output(CMD, shell=True, timeout=4000)
        except subprocess.TimeoutExpired as exc:
            print("GATOR timed out: {}".format(exc))
            return
        except subprocess.CalledProcessError as e:
            out_bytes = e.output 
            code = e.returncode
        out_text = out_bytes.decode('utf-8')
        # print("out_text:", out_text)
        res = re.findall(r'XML\s+file:\s+(\S+)\s+', out_text)
        if res:
            xml_file = res[0]
            # print("XML file: ", xml_file)
            subprocess.call(["cp", xml_file, new_gator_file])
        else:
            print("No XML.")

    def start(self):
        apklist = getFileList(APKPATH, ".apk")
        args = [(apk) for apk in apklist]
        pool = threadpool.ThreadPool(DEFAULT_MAX_JOB)
        requests = threadpool.makeRequests(self.call_gator, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        print("args: ", args)
        print("GUI widgets extraction completed.")
