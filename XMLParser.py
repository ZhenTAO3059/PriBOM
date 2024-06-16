#!/usr/bin/env python3
import threadpool
from Common import *
import xml.etree.ElementTree as ET
import csv


class XMLParser:
    def __init__(self):
        self.HEADER = ["view type", "view id", "view idname", "event and handler"]

    def remove_dup(self, a):
        b = []
        for item in a:
            if item not in b:
                b.append(item)
        return b

    def parse_onetree(self, in_file):
        csv_path = CSVPATH + "/" + os.path.split(in_file)[-1][:-4] + ".csv"
        if os.path.exists(csv_path):
            return

        res = []
        try:
            tree = ET.parse(in_file)
            root = tree.getroot()

            for view in root.iter('View'):

                view_record = []
                view_attr = view.attrib
                view_record.append(view_attr.get('type', 'None'))
                view_record.append(view_attr.get('id', 'None'))
                view_record.append(view_attr.get('idName', 'None'))

                for event in view.findall('EventAndHandler'):
                    event_attr = event.attrib
                    view_record.append(event_attr.get('event', 'None'))
                    view_record.append(event_attr.get('handler', 'None'))
                res.append(view_record)

                if view_record[1] != "None":
                    print("view_record: ", view_record)

            res = self.remove_dup(res)

            with open(csv_path, 'w', newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADER)
                for item in res:
                    writer.writerow(item)

        except Exception as e:
            print(f"Error occurred while parsing {in_file}: {e}")

    def start(self):
        xmllist = getFileList(XMLPATH, ".xml")
        print("[+] Parsing " + str(len(xmllist)) + " XML files...")
        args = [(xml) for xml in xmllist]
        pool = threadpool.ThreadPool(DEFAULT_MAX_JOB)
        requests = threadpool.makeRequests(self.parse_onetree, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()
