from graph_building.graph_builder import build_graph
from graph_building.parse_yolo_result import parse_res
from ocr_module.ocr import ocrLocal
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os
import re

import cv2
import numpy as np

import sys
import subprocess
import pickle

from graph_building.parser import GILBRETH_PARSER, Tree2AST

import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('flowchart_image', help="path to the flowchart image")
argparser.add_argument('--annotations_cache', help="path to the annotations pickle", default=None)
argparser.add_argument('--graph_cache', help="path to the graph pickle", default=None)

args = argparser.parse_args()

def print_hor_sep():
    _, cols = os.popen('stty size', 'r').read().split()

    for _ in range(int(cols)):
        print("-", end="")
    print()

def is_subbox(little_box, big_box):
    return little_box[0][0] >= big_box[0][0] and little_box[0][1] >= big_box[0][1] and little_box[3][0] <= big_box[3][0] and little_box[3][1] <= big_box[3][1]

def fill_graph_text(graph, annotations):
    for node in graph.nodes:
        if node.text_content == "NOT SUPPORTED YET":
            node.text_content = ""
        for block in annotations.pages[0].blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        annotation_coords = []
                        annotation_coords.append((symbol.bounding_box.vertices[0].x, symbol.bounding_box.vertices[0].y))
                        annotation_coords.append((symbol.bounding_box.vertices[1].x, symbol.bounding_box.vertices[1].y))
                        annotation_coords.append((symbol.bounding_box.vertices[3].x, symbol.bounding_box.vertices[3].y))
                        annotation_coords.append((symbol.bounding_box.vertices[2].x, symbol.bounding_box.vertices[2].y))

                        if is_subbox(annotation_coords, node.shape.coords):
                            node.text_content += symbol.text
                            if symbol.property.detected_break.type == 0:
                                pass
                            elif symbol.property.detected_break.type == 1 or symbol.property.detected_break.type == 3:
                                node.text_content += " "
                            else:
                                node.text_content += " "

flowchart_image = args.flowchart_image
print("IMAGE TO PROCESS: " + flowchart_image)

if args.graph_cache is None:
    print("Detecting Shapes for" + flowchart_image)
    cmd = "./deep_learning/darknet/darknet detector test ./fc_dirs/obj.data ./deep_learning/yolov3-tiny.cfg ./deep_learning/yolov3-tiny_best.weights".split() + [flowchart_image] + "-dont_show -ext_output > result-shapes.txt".split()
    print(cmd)
    shape_detection_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, err = shape_detection_process.communicate()

    if err is not None:
        print("UNEXPECTED ERROR")
        print(err)
        exit(-1)
    else:
        with open("result-shapes.txt", "wb") as res_shape:
            res_shape.write(output)

    print("Detecting Arrows")
    cmd = "./deep_learning/darknet/darknet detector test ./fc_dirs/obj-lines.data ./deep_learning/yolov3-spp.cfg ./deep_learning/yolov3-spp_11000.weights".split() + [ flowchart_image ] + " -dont_show -ext_output > result-lines.txt".split()
    line_detection_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, err = line_detection_process.communicate()

    if err is not None:
        print("UNEXPECTED ERROR")
        print(err)
        exit(-1)
    else:
        with open("result-lines.txt", "wb") as res_lines:
            res_lines.write(output)

    shapes_pred = parse_res("result-shapes.txt")
    lines_pred = parse_res("result-lines.txt")
    bboxes = []
    for shape in shapes_pred:
        c = [ list(x) for x in shape.coords ]
        c[0][0] -= 15
        c[0][1] -= 15
        c[1][0] += 15
        c[1][1] -= 15
        c[2][0] -= 15
        c[2][1] += 15
        c[3][0] += 15
        c[3][1] += 15

        c = [ tuple(x) for x in c ]

        bboxes.append(c)

    for line in lines_pred:
        c = [ list(x) for x in line.coords ]
        c[0][0] -= 15
        c[0][1] -= 15
        c[1][0] += 15
        c[1][1] -= 15
        c[2][0] -= 15
        c[2][1] += 15
        c[3][0] += 15
        c[3][1] += 15

        c = [ tuple(x) for x in c ]

        bboxes.append(c)


    graph = build_graph("result-lines.txt", "result-shapes.txt")

    if args.annotations_cache is None:
        # print("\n\n\033[91m\033[1mWARNING: Using Google Vision API to detect text.\n"+
        #     "This stuff costs us money, so use the --annotations_cache option next time.\nPaise ka ped nahi hai hamare paas...\033[0m")

        warning_process = subprocess.Popen('cowsay -g "WARNING: Using Google Vision API to detect text. This stuff costs us money, so use the --annotations_cache option next time. Paise ka ped nahi hai hamare paas..."'.split())
        output, err = warning_process.communicate()

        ann = ocrLocal(flowchart_image)
        annotations = ann.full_text_annotation
        # print("Annotations:")
        # print(annotations)
        with open("fullannotations.pickle", "wb") as annotations_pickle:
            pickle.dump(annotations, annotations_pickle)

    else:
        with open(args.annotations_cache, "rb") as annotations_pickle:
            print("Loading annotations from cache. Thanks for saving us money.")
            annotations = pickle.load(annotations_pickle)
            print("Loaded annotations")

    fill_graph_text(graph, annotations)

    print("\n\n")


    print_hor_sep()
    print("\n\n")

    print("We have tried as hard as we can to detect your graph. If we have made any mistakes, we ask for your forgiveness. You will have a chance to make your corrections later on.\n")
    print(graph)

    im = np.array(Image.open(flowchart_image), dtype=np.uint8)
    fig,ax = plt.subplots(1)
    ax.imshow(im)
    for node in graph.nodes:
        node_coords = node.shape.coords
        rect = patches.Rectangle(node_coords[0],
            abs(node_coords[0][0] - node_coords[1][0]),
            abs(node_coords[0][1] - node_coords[2][1]),
            linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        plt.text(node_coords[0][0] + 10, node_coords[0][1] - 10, node.shape.obj_id, color='b')
    plt.show(block=False)

    print("\n\nMake changes if needed:")
    print("\nNodes:")

    for i in range(len(graph.nodes)):
        print("Node ID: " + graph.nodes[i].shape.obj_id)
        print("Detected Contents: " + graph.nodes[i].text_content)
        print("Corrected Contents (press ENTER if no corrections): ", end="")
        c = input()
        if c != "":
            graph.nodes[i].text_content = c
            print("Correction recorded")

    print("\nControl Flow:")
    for flow in graph.control_flow:
        print("Control Flow: " + str(flow))
        while True:
            print("Delete Flow? (y/N): ", end="")
            c = input()
            if c in "nN" or c == "":
                print()
                break
            elif c in "yY":
                graph.control_flow.remove(flow)
                print("Flow", flow, "removed")
                print()
                break
            else:
                print("Enter y or n")
            print()

    node_ids = [ node.shape.obj_id for node in graph.nodes ]
    while True:
        c = input("\nDo you want to enter additional flows?(y/N): ")
        if c == "" or c in "nN":
            break
        elif c in "yY":
            flowstr = input("Enter the control flow as `source_id, dest_id`: ")
            flow = re.split(r'[, ]+', flowstr)
            if len(flow) == 2 and all(_id in node_ids for _id in flow):
                graph.control_flow.append(flow)
            else:
                print("Invalid control flow")
        else:
            print("Enter y or n")

    print("\nNoted. Thanks for putting up with us :-)\n\n")

    print_hor_sep()

    graph.clean()

    print("\n\nFinal Graph:\n")
    print(graph)
    plt.show()

    print_hor_sep()

    # Adding the AST to each node
    for i in range(len(graph.nodes)):
        parse_tree = GILBRETH_PARSER.parse(graph.nodes[i].text_content)
        parse_tree = Tree2AST(parse_tree).gen_AST()
        graph.nodes[i].PT = parse_tree
    
    print("Saving the final graph to graph.pickle")
    with open("graph.pickle", "wb") as graph_pickle:
        pickle.dump(graph, graph_pickle)

    print("Graph Saved")
else:
    print("Loading Graph:")
    with open(args.graph_cache, "rb") as graph_pickle:
        graph = pickle.load(graph_pickle)
        print("Loaded graph")

print(graph)