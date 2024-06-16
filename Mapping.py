import csv
import os
import androguard
from androguard.misc import AnalyzeAPK
from Common import *
from networkx import DiGraph
import networkx as nx
import subprocess
import shlex

def parse_call_method(call_method_str):

    trimmed = call_method_str.strip('<>')

    parts = trimmed.split(':')
    if len(parts) != 2:
        raise ValueError("Unexpected format for call method string")

    # Extract class name and method signature
    class_name_part = parts[0].strip()
    method_signature = parts[1].strip()

    # Transform class name into the desired format
    class_name = 'L' + class_name_part.replace('.', '/') + ';'

    # Extract method name from the method signature
    method_name = method_signature.split(' ')[1].split('(')[0]

    return class_name, method_name

def extract_data_from_row(row):
    methods = []
    for i in range(3, len(row), 2):
        if i+1 < len(row):
            methods.append(row[i+1])  # 'call method' column
    return row[:3], methods

def get_all_called_methods(dx, class_name, method_name, visited, max_depth=20):
    if (class_name, method_name) in visited:
        return

    visited.add((class_name, method_name))
    call_graph = dx.get_call_graph(classname=class_name, methodname=method_name)

    if call_graph.number_of_edges() == 0:
        return

    for _, callee, _ in call_graph.edges(data=True):
        callee_class, callee_method = parse_method(callee)
        get_all_called_methods(dx, callee_class, callee_method, visited, max_depth - 1)

def parse_method(full_method_name):

    # Extract the class name and method name from the full method name
    parts = str(full_method_name).split('->')
    class_name = parts[0]
    method_name = parts[1].split('(')[0]
    return class_name, method_name

def generate_full_call_graph(dx):

    # Generate the complete call graph for the entire APK.
    full_call_graph = DiGraph()
    for method in dx.get_methods():
        class_name, method_name = method.class_name, method.name
        method_call_graph = dx.get_call_graph(classname=class_name, methodname=method_name)
        full_call_graph = nx.compose(full_call_graph, method_call_graph)
    return full_call_graph

def generate_full_call_graph_from_cli(apk_path, output_dir='./Callgraph'):

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct the output file path
    apk_name = os.path.basename(apk_path)
    output_file = os.path.join(output_dir, f"{apk_name}.gml")

    # Run the Androguard command
    command = f"python3 ~/androguard/androguard/cli/cli.py cg -o {shlex.quote(output_file)} {shlex.quote(apk_path)}"
    subprocess.run(command, shell=True, check=True)

    print(f"call graph saved to {output_file}")

    graph = nx.read_gml(output_file)

    return graph


def get_mappings(permissionMap):

    # Loop through all CSV files in the directory
    for csv_file in os.listdir(CSVPATH):
        if csv_file.endswith('.csv'):
            apk_name = csv_file.replace('.csv', '.apk')
            apk_path = os.path.join(APKPATH, apk_name)
            csv_path = os.path.join(CSVPATH, csv_file)

            if "xender" not in apk_name:
                continue

            mapping_list = []

            a, d, dx = AnalyzeAPK(apk_path)

            # only needed for stragety 2
            # option 1
            # full_call_graph = generate_full_call_graph(dx)

            # option 2
            full_call_graph = generate_full_call_graph_from_cli(apk_path)

            with open(csv_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    other_columns, methods = extract_data_from_row(row)
                    for method in methods:

                        all_methods = set()

                        # Extract class name and method name from the 'call method'
                        class_name, method_name = parse_call_method(method)
                        
                        # call_graph = dx.get_call_graph(classname=class_name, methodname=method_name)


                        # strategy 1: Recursively Calling dx.get_call_graph
                        # get_all_called_methods(dx, class_name, method_name, all_methods)

                        # stragtegy 2: Generating the Complete Call Graph of the APK

                        # option 1
                        # this_method = None
                        # for m in dx.get_methods():
                        #     if m.class_name in method and m.name in method:
                        #         this_method = m
                        #         break
                        # for edge in nx.dfs_edges(full_call_graph, this_method):
                        #     all_methods.add((edge[1].class_name, edge[1].name))  # Add the destination method of each edge

                        # option 2
                        this_method = None
                        for m in dx.get_methods():
                            if m.class_name in method and m.name in method:
                                this_method = m
                                break
                        for edge in nx.dfs_edges(full_call_graph, this_method):
                            dst_class, dst_method = parse_method(edge[1])
                            all_methods.add((dst_class, dst_method))

                        for mc, mn in all_methods:
                            for k, v in permissionMap.items():
                                if mc in k and mn in k:
                                    mapping_list.append([other_columns[0], other_columns[1], other_columns[2], k, v])
            
            # print("mapping_list: ", mapping_list)
            # print("lem of mapping_list: ", len(mapping_list))

            headers = ['widget type', 'widget id', 'widget name', 'method', 'permission']
            mapping_file = MAPPINGPATH + '/' + apk_name + '.csv'

            with open(mapping_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)

                for row in mapping_list:
                    writer.writerow(row)

            print(f"Data written to {mapping_file}")

                    