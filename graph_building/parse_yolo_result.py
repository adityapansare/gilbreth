class ResObj:
    def __init__(self):
        self.obj_id = None
        self.obj_type = None
        self.coords = None

    def add_coords(self, dim):
        self.coords = []
        self.coords.append((dim[0], dim[1]))
        self.coords.append((dim[0] + dim[2], dim[1]))
        self.coords.append((dim[0], dim[1] + dim[3]))
        self.coords.append((dim[0] + dim[2], dim[1] + dim[3]))
    
    def __repr__(self):
        return "{ id: " + self.obj_id + ", type: " + self.obj_type + ", coords: " + self.coords.__repr__() + " }"

def parse_res(filename : str):
    objs = []
    with open(filename) as res_file:
        content = res_file.readlines()
        shape_count = {}
        for line in content[3:]:
            obj = ResObj()
            obj.obj_type = line[:line.find(":")]
            obj.add_coords([ int(s) for s in line[:-2].split() if s.isdigit() ])
            if obj.obj_type not in shape_count:
                shape_count[obj.obj_type] = 0
            obj.obj_id = obj.obj_type + "_" + str(shape_count[obj.obj_type])
            objs.append(obj)
            shape_count[obj.obj_type] += 1
    
    return objs