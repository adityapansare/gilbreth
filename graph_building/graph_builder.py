from graph_building.parse_yolo_result import parse_res
# from ocr_module.ocr import ocrLocal
from graph_building.constants import *
import sys


# annotations = ocrLocal(sys.argv[1]).text_annotations

# lines = parse_res("../deep_learning/result-lines-22.txt")
# shapes = parse_res("../deep_learning/result-shapes-22.txt")

class CFGNode:
    def __init__(self):
        self.shape = None
        self.text_content = None
        self.PT = None
        
    def __repr__(self):
        return self.shape.obj_id + ":\n\t" + self.text_content + "\n\tParse Tree: " + str(self.PT)

class CFG:
    def __init__(self):
        self.nodes = []
        self.control_flow = []
    def __repr__(self):
        # return self.nodes.__repr__() + "\n" + self.control_flow.__repr__()
        repr_str = ""
        for node in self.nodes:
            repr_str += node.__repr__() + "\n"
        for flow in self.control_flow:
            repr_str += str(flow) + "\n"
        return repr_str

    def clean(self):
        # n_list = list(self.nodes)
        for node in self.nodes:
            if not any(node.shape.obj_id in flow for flow in self.control_flow):
                # print(node)
                self.nodes.remove(node)

def find_inedges(shape, lines):
    inedges = {}
    for line in lines:
        if line.obj_type == "down_arrow":
            arrow_end = ((line.coords[2][0] + line.coords[3][0]) / 2, line.coords[2][1])
            top_coords = shape.coords[:2]
            top_y = top_coords[0][1]
            bottom_y = shape.coords[2][1]
            if top_y - BOUNDINGTHRESHOLD <= arrow_end[1] and arrow_end[1] <= bottom_y + BOUNDINGTHRESHOLD and top_coords[0][0] <= arrow_end[0] and arrow_end[0] <= top_coords[1][0]:
                inedges[line] = arrow_end
        elif line.obj_type == "up_arrow":
            arrow_end = ((line.coords[0][0] + line.coords[1][0]) / 2, line.coords[0][1])
            bottom_coords = shape.coords[2:]
            top_y = shape.coords[0][1]
            bottom_y = bottom_coords[0][1]
            if top_y - BOUNDINGTHRESHOLD <= arrow_end[1] and arrow_end[1] <= bottom_y + BOUNDINGTHRESHOLD and bottom_coords[0][0] <= arrow_end[0] and arrow_end[0] <= bottom_coords[1][0]:
                inedges[line] = arrow_end
        elif line.obj_type == "right_arrow":
            arrow_end = (line.coords[1][0], (line.coords[1][1] + line.coords[3][1]) / 2)
            left_coords = shape.coords[0::2]
            left_x = left_coords[0][0]
            right_x = shape.coords[1][0]
            if left_x - BOUNDINGTHRESHOLD <= arrow_end[0] and arrow_end[0] <= right_x + BOUNDINGTHRESHOLD and left_coords[0][1] <= arrow_end[1] and arrow_end[1] <= left_coords[1][1]:
                inedges[line] = arrow_end
        elif line.obj_type == "left_arrow":
            arrow_end = (line.coords[0][0], (line.coords[0][1] + line.coords[2][1]) / 2)
            right_coords = shape.coords[1::2]
            left_x = shape.coords[0][0]
            right_x = right_coords[0][0]
            if left_x - BOUNDINGTHRESHOLD <= arrow_end[0] and arrow_end[0] <= right_x + BOUNDINGTHRESHOLD and right_coords[0][1] <= arrow_end[1] and arrow_end[1] <= right_coords[1][1]:
                inedges[line] = arrow_end
    return inedges

# function backtrack(edgelist):         // edgelist will be a dict with the edge as the key and the coord from where backtracking starts as the value
# for each edge in edgelist
#   remove current edge from the edgelist
#   find intersecting edges
#   add each intersecting edge and its intersecting coord to the edgelist
#   if a shape is encountered, add the shape to the final shapelist
# return shapelist

def get_intersecting_edges(edge, lines):
    # print("CHECKING INTERSECTION FOR", edge)
    intersecting = {}
    for line in lines:
        if line != edge:
            if line.obj_type == "down_arrow":
                # arrow end must intersect
                arrow_end = ((line.coords[2][0] + line.coords[3][0]) / 2, line.coords[2][1])
                if abs(arrow_end[1] - edge.coords[0][1]) <= LINETHRESHOLD and edge.coords[0][0] - LINETHRESHOLD <= arrow_end[0] and arrow_end[0] <= edge.coords[1][0] + LINETHRESHOLD:
                    intersecting[line] = arrow_end
            elif line.obj_type == "up_arrow":
                # arrow end must intersect
                arrow_end = ((line.coords[0][0] + line.coords[1][0]) / 2, line.coords[0][1])
                if abs(arrow_end[1] - edge.coords[2][1]) <= LINETHRESHOLD and edge.coords[2][0] - LINETHRESHOLD <= arrow_end[0] and arrow_end[0] <= edge.coords[3][0] + LINETHRESHOLD:
                    intersecting[line] = arrow_end
            elif line.obj_type == "left_arrow":
                # arrow end must intersect
                arrow_end = (line.coords[0][0], (line.coords[0][1] + line.coords[2][1]) / 2)
                if abs(arrow_end[0] - edge.coords[1][0]) <= LINETHRESHOLD and edge.coords[1][1] - LINETHRESHOLD <= arrow_end[1] and arrow_end[1] <= edge.coords[3][1] + LINETHRESHOLD:
                    intersecting[line] = arrow_end
            elif line.obj_type == "right_arrow":
                # arrow end must intersect
                arrow_end = (line.coords[1][0], (line.coords[1][1] + line.coords[3][1]) / 2)
                if abs(arrow_end[0] - edge.coords[0][0]) <= LINETHRESHOLD and edge.coords[0][1] - LINETHRESHOLD <= arrow_end[1] and arrow_end[1] <= edge.coords[2][1] + LINETHRESHOLD:
                    intersecting[line] = arrow_end
            elif line.obj_type == "horizontal_line":
                # any end can intersect
                # restrict it such that only intersections can be at 90 degrees
                left_end = (line.coords[0][0], (line.coords[0][1] + line.coords[2][1]) / 2)
                right_end = (line.coords[1][0], (line.coords[1][1] + line.coords[3][1]) / 2)
                # print("HORIZONTAL", left_end, right_end)
                # if (abs(left_end[0] - edge.coords[1][0]) <= LINETHRESHOLD or abs(left_end[0] - edge.coords[0][0]) <= LINETHRESHOLD) and edge.coords[1][1] - LINETHRESHOLD <= left_end[1] and left_end[1] <= edge.coords[3][1] + LINETHRESHOLD:
                if (edge.coords[0][0] - LINETHRESHOLD <= left_end[0] and edge.coords[1][0] + LINETHRESHOLD >= left_end[0]) and edge.coords[1][1] - LINETHRESHOLD <= left_end[1] and left_end[1] <= edge.coords[3][1] + LINETHRESHOLD:
                    intersecting[line] = left_end
                # elif (abs(right_end[0] - edge.coords[0][0]) <= LINETHRESHOLD or abs(right_end[0] - edge.coords[1][0]) <= LINETHRESHOLD) and edge.coords[0][1] - LINETHRESHOLD <= right_end[1] and right_end[1] <= edge.coords[2][1] + LINETHRESHOLD:
                elif (edge.coords[0][0] - LINETHRESHOLD <= right_end[0] and right_end[0] <= edge.coords[1][0] + LINETHRESHOLD) and edge.coords[0][1] - LINETHRESHOLD <= right_end[1] and right_end[1] <= edge.coords[2][1] + LINETHRESHOLD:
                    intersecting[line] = right_end
                elif left_end[0] - LINETHRESHOLD <= edge.coords[0][0] and edge.coords[1][0] <= right_end[0] + LINETHRESHOLD and ((line.coords[0][1] - LINETHRESHOLD <= edge.coords[0][1] and edge.coords[0][1] <= line.coords[2][1] + LINETHRESHOLD) or (line.coords[0][1] - LINETHRESHOLD <= edge.coords[2][1] and edge.coords[2][1] <= line.coords[2][1] + LINETHRESHOLD)):
                    intersecting[line] = ()
            elif line.obj_type == "vertical_line":
                # any end can intersect
                # restrict it such that only intersections can be at 90 degrees
                top_end = ((line.coords[0][0] + line.coords[1][0]) / 2, line.coords[0][1])
                bottom_end = ((line.coords[2][0] + line.coords[3][0]) / 2, line.coords[2][1])
                # print("TOP", top_end)
                # print("BOTTOM", bottom_end)
                # print(edge)
                # if (abs(top_end[1] - edge.coords[2][1]) <= LINETHRESHOLD or abs(top_end[1] - edge.coords[0][1]) <= LINETHRESHOLD) and edge.coords[2][0] - LINETHRESHOLD <= top_end[0] and top_end[0] <= edge.coords[3][0] + LINETHRESHOLD:
                if (edge.coords[0][1] - LINETHRESHOLD <= top_end[1] and top_end[1] <= edge.coords[2][1] + LINETHRESHOLD) and edge.coords[2][0] - LINETHRESHOLD <= top_end[0] and top_end[0] <= edge.coords[3][0] + LINETHRESHOLD:
                    intersecting[line] = top_end
                # elif (abs(bottom_end[1] - edge.coords[0][1]) <= LINETHRESHOLD or abs(bottom_end[1] - edge.coords[2][1]) <= LINETHRESHOLD) and edge.coords[0][0] - LINETHRESHOLD <= bottom_end[0] and bottom_end[0] <= edge.coords[1][0] + LINETHRESHOLD:
                elif (edge.coords[0][1] - LINETHRESHOLD <= bottom_end[1] and bottom_end[1] <= edge.coords[2][1] + LINETHRESHOLD) and edge.coords[0][0] - LINETHRESHOLD <= bottom_end[0] and bottom_end[0] <= edge.coords[1][0] + LINETHRESHOLD:
                    intersecting[line] = bottom_end
                elif top_end[1] - LINETHRESHOLD <= edge.coords[0][1] and edge.coords[2][1] <= bottom_end[1] + LINETHRESHOLD and ((line.coords[0][0] - LINETHRESHOLD <= edge.coords[0][0] and edge.coords[0][0] <= line.coords[1][0] + LINETHRESHOLD) or (line.coords[0][0] - LINETHRESHOLD <= edge.coords[1][0] and edge.coords[1][0] <= line.coords[1][0] + LINETHRESHOLD)):
                    intersecting[line] = ()
    return intersecting

def getSourceShape(edgedict : dict, shapes):
    dest_pt = list(edgedict.values())[0]
    edge = list(edgedict.keys())[0]

    if edge.obj_type == "down_arrow":
        src_point = ((edge.coords[0][0] + edge.coords[1][0])/2 , edge.coords[0][1])
        for shape in shapes:
            bottom_coords = shape.coords[2:]
            bottom_y = bottom_coords[0][1]
            top_y = shape.coords[0][1]
            if top_y - BOUNDINGTHRESHOLD <= src_point[1] and src_point[1] <= bottom_y + BOUNDINGTHRESHOLD and src_point[0] >= bottom_coords[0][0] and src_point[0] <= bottom_coords[1][0]:
                return [shape]
    elif edge.obj_type == "up_arrow":
        src_point = ((edge.coords[2][0] + edge.coords[3][0])/2 , edge.coords[2][1])
        for shape in shapes:
            top_coords = shape.coords[:2]
            top_y = top_coords[0][1]
            bottom_y = shape.coords[2][1]
            if top_y - BOUNDINGTHRESHOLD <= src_point[1] and src_point[1] <= bottom_y + BOUNDINGTHRESHOLD and src_point[0] >= top_coords[0][0] and src_point[0] <= top_coords[1][0]:
                return [shape]
    elif edge.obj_type == "left_arrow":
        src_point = (edge.coords[1][0], (edge.coords[1][1] + edge.coords[3][1]) / 2)
        for shape in shapes:
            left_coords = shape.coords[0::2]
            left_x = left_coords[0][0]
            right_x = shape.coords[1][0]
            if left_x - BOUNDINGTHRESHOLD <= src_point[0] and src_point[0] <= right_x + BOUNDINGTHRESHOLD and src_point[1] >= left_coords[0][1] and src_point[1]<=left_coords[1][1]:
                return [shape]
    elif edge.obj_type == "right_arrow":
        src_point = (edge.coords[0][0], (edge.coords[0][1] + edge.coords[2][1]) / 2)
        for shape in shapes:
            right_coords = shape.coords[1::2]
            right_x = right_coords[0][0]
            left_x = shape.coords[0][0]
            if left_x - BOUNDINGTHRESHOLD <= src_point[0] and src_point[0] <= right_x + BOUNDINGTHRESHOLD and src_point[1] >= right_coords[0][1] and src_point[1]<=right_coords[1][1]:
                return [shape]
    elif edge.obj_type == "horizontal_line":
        left_pt = (edge.coords[0][0], (edge.coords[0][1] + edge.coords[2][1]) / 2)
        right_pt = (edge.coords[1][0], (edge.coords[1][1] + edge.coords[3][1]) / 2)

        shape_src = []
        # print("Horizontal", left_pt, right_pt)
        # if dest_pt == left_pt:
        src_point = right_pt
        for shape in shapes:
            # print(shape)
            left_coords = shape.coords[0::2]
            left_x = left_coords[0][0]
            right_x = shape.coords[1][0]
            if left_x - BOUNDINGTHRESHOLD <= src_point[0] and src_point[0] <= right_x + BOUNDINGTHRESHOLD and src_point[1] >= left_coords[0][1] and src_point[1]<=left_coords[1][1]:
                shape_src.append(shape)
        # elif dest_pt == right_pt:
        src_point = left_pt
        for shape in shapes:
            right_coords = shape.coords[1::2]
            right_x = right_coords[0][0]
            left_x = shape.coords[0][0]
            if left_x - BOUNDINGTHRESHOLD <= src_point[0] and src_point[0] <= right_x + BOUNDINGTHRESHOLD and src_point[1] >= right_coords[0][1] and src_point[1]<=right_coords[1][1]:
                shape_src.append(shape)
        # print("SHAPE SRC", shape_src)
        if len(shape_src):
            return shape_src
    elif edge.obj_type == "vertical_line":
        top_pt = ((edge.coords[0][0] + edge.coords[1][0])/2 , edge.coords[0][1])
        bottom_pt = ((edge.coords[2][0] + edge.coords[3][0])/2 , edge.coords[2][1])
        
        shape_src = []

        # if dest_pt == top_pt:
        src_point = bottom_pt
        for shape in shapes:
            top_coords = shape.coords[:2]
            top_y = top_coords[0][1]
            bottom_y = shape.coords[2][1]
            if top_y - BOUNDINGTHRESHOLD <= src_point[1] and src_point[1] <= bottom_y + BOUNDINGTHRESHOLD and src_point[0] >= top_coords[0][0] and src_point[0] <= top_coords[1][0]:
                shape_src.append(shape)
        # elif dest_pt == bottom_pt:
        src_point = top_pt
        for shape in shapes:
            bottom_coords = shape.coords[2:]
            bottom_y = bottom_coords[0][1]
            top_y = shape.coords[0][1]
            if top_y - BOUNDINGTHRESHOLD <= src_point[1] and src_point[1] <= bottom_y + BOUNDINGTHRESHOLD and src_point[0] >= bottom_coords[0][0] and src_point[0] <= bottom_coords[1][0]:
                shape_src.append(shape)
        
        if len(shape_src):
            return shape_src
    else:
        return None

def backtracking(edgelist, lines, shapes, visited = []):
    predecessors = []
    for edge in edgelist:
        # print("EDGE", edge)
        int_edges = get_intersecting_edges(edge, lines)
        for visited_edge in visited:
            int_edges.pop(visited_edge, None)
        # print("INTERSECTIONS", int_edges)
        visited.append(edge)
        if len(int_edges) == 0:
            # print(getSourceShape({edge: edgelist[edge]}))
            # print("EDGEOUT", {edge: edgelist[edge]})
            e = {edge: edgelist[edge]}
            predecessors += getSourceShape(e, shapes)
        else:
            p = getSourceShape({edge: edgelist[edge]}, shapes)
            if p is not None and len(p):
                predecessors += p
            for pred_edge in int_edges:
                predecessors += backtracking({pred_edge: int_edges[pred_edge]}, lines, shapes, visited)
    return predecessors

def build_graph(line_txt: str, shape_txt: str):
    lines = parse_res(line_txt)
    shapes = parse_res(shape_txt)
    graph = CFG()

    for shape in shapes:
        # print("SHAPE", shape)
        # print(shape)
        shape_node = CFGNode()
        shape_node.shape = shape
        shape_node.text_content = "NOT SUPPORTED YET"
        graph.nodes.append(shape_node)
        inedges = find_inedges(shape, lines)
        # print("INEDGES", inedges)
        for edge in inedges:
            # print("EDGEOUT", inedges)
            pred_shapes = backtracking({edge : inedges[edge]}, lines, shapes)
            # print("Predecessors to", shape, "are", pred_shapes)
            for pred in pred_shapes:
                graph.control_flow.append([pred.obj_id, shape.obj_id])

    # print(graph)
    graph.clean()
    return graph