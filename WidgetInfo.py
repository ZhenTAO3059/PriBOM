import subprocess
import threadpool
from Common import *
import csv
import re
import shutil
from JADXdecompile import decompile_apk
import shlex


class WidgetInfo:
    def solve_one(self, csvfile):
        apkname = os.path.split(csvfile)[-1][:-4]
        print("[+] Mapping " + apkname)
        output_set = os.path.join(InfoSet, apkname + ".csv")

        valid_rows = self.get_valid_lines(csvfile)
        # print("len of valid_rows: ", len(valid_rows))

        if not valid_rows:
            return
        if not os.path.exists(os.path.join(JADXPATH, apkname)):
            decompile_apk(os.path.join(APKPATH, apkname + ".apk"))

        if not os.path.exists(os.path.join(JADXPATH, apkname)):
            print("no jadx dir.")
            return

        jadxfilelist = getFileList(os.path.join(JADXPATH, apkname), "")

        with open(output_set, "w", newline="") as fw:
            writer = csv.writer(fw)
            for row in valid_rows:
                ID = row[1]
                IDname = row[2]

                pic_path, text_of_icon = self.get_icon_text(IDname, JADXPATH, apkname)

                print(f"pic_path: {pic_path}, text_of_icon: {text_of_icon}")

                if not pic_path:
                    continue

                PIC_NAME = ";".join(pic_path)
                ICON_TYPE = row[0]
                pics = []
                for item in pic_path:
                    subpaths = item.strip("@").split("/")
                    folder = subpaths[0]
                    filename = subpaths[-1]
                    for f in jadxfilelist:
                        if filename + "." in f and folder in f:
                            pics.append(f)

                if not pics:
                    continue 

                PIC_TRUE_PATH = ";".join(pics)
                TEXT_Of_ICON = text_of_icon

                handlers = []
                events = []
                length = len(row)
                if length - 2 < 3:
                    continue

                for i in range(3, length):
                    if i % 2 == 0:
                        handlers.append(row[i])
                    else:
                        events.append(row[i])

                writer.writerow([PIC_NAME, IDname, ICON_TYPE, TEXT_Of_ICON,
                                 apkname, ";".join(events), ";".join(handlers), PIC_TRUE_PATH])

        shutil.rmtree(os.path.join(JADXPATH, apkname))
        if not os.path.getsize(output_set):
            os.remove(output_set)

    def get_valid_lines(self, csvfile):
        res = []
        with open(csvfile, "r") as f:
            reader = csv.reader(f)
            rows = [row for row in reader]
        for row in rows[1:]: 
            if len(row) > 4:
                res.append(row)
        return res

    def get_icon_text(self, IDname, JADXPATH, apkname):
        try:
            escaped_apkname = shlex.quote(apkname)
            escaped_IDname = shlex.quote(IDname)
            CMD = "grep -r id/" + escaped_IDname + " " + JADXPATH + "/" + escaped_apkname
            out_bytes = subprocess.check_output(CMD, shell=True)
        except subprocess.CalledProcessError as e:
            out_bytes = e.output 
            code = e.returncode
        out_text = out_bytes.decode('utf-8')

        possible_path = []
        contentDescription = ""
        res = re.findall(r'android:src="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])
        res = re.findall(r'android:background="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])
        res = re.findall(r'android:drawableRight="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])
        res = re.findall(r'android:drawableTop="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])
        res = re.findall(r'android:drawableLeft="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])
        res = re.findall(r'android:drawableBottom="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])
        res = re.findall(r'android:drawableEnd="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])
        res = re.findall(r'android:drawableStart="(\S+)"', out_text)
        if res:
            possible_path.append(res[0])

        res = re.findall(r'android:contentDescription="(\S+)"', out_text)
        if res:
            contentDescription = res[0]

        return possible_path, contentDescription

    def start(self):
        csvfiles = getFileList(CSVPATH, ".csv")
        args = [(file) for file in csvfiles if "xender" in file]
        pool = threadpool.ThreadPool(DEFAULT_MAX_JOB)
        requests = threadpool.makeRequests(self.solve_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()
