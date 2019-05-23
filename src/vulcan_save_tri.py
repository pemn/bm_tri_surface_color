#!python
# Copyright 2019 Vale
# save a triangulation in vulcan format
# binary or ascii

import numpy as np
import os.path
import skimage.io

def vulcan_save_asc(nodes, faces, output):
  of = open(output, 'w')
  for i in range(3):
    print("%-24s" % "Created External", file=of)

  print("No Points: %d, No Triangles: %d" % (len(nodes), len(faces)), file=of)
  for n in nodes:
    print("Vertex: %16.4f, %16.4f, %16.4f" % tuple(n), file=of)
  for f in faces:
    print("Index : %06d, %06d, %06d" % tuple(np.add(f,(1,1,1))), file=of)



def vulcan_save_tri(nodes, faces, output):
  import vulcan
  tri = vulcan.triangulation("", "w")
  tri.set_colour(1)
  for k in nodes:
    tri.add_node(*k)
  for k in faces:
    tri.add_face(*map(int, k))
  tri.save(output)

# por each vertex, create a texture mapping node
def vulcan_texture_vt(cols, rows):
  x_grid, y_grid = np.meshgrid(np.linspace(0, 1, rows), np.linspace(1, 0, cols))
  return np.column_stack((x_grid.flat, y_grid.flat))

# save a triangulation as a Wavefront OBJ (obj, mtl, png)
def vulcan_save_obj(nodes, faces, texture, output_path, rows_cols = None):
  # obj file
  of = open(output_path, 'w')
  output_mtl = os.path.splitext(output_path)[0] + '.mtl'

  print("mtllib", output_mtl, file=of)
  print("usemtl material0", file=of)
  for n in nodes:
    print("v %f %f %f" % tuple(n), file=of)

  if rows_cols is not None:
    for uv in vulcan_texture_vt(*rows_cols):
      print("vt %f %f" % tuple(uv.tolist()), file=of)

  for f in faces:
    face1 = np.add(f,(1,1,1))
    print("f %d/%d %d/%d %d/%d" % tuple(np.column_stack((face1, face1)).flat), file=of)

  of.close()
  # tif file
  output_img = os.path.splitext(output_path)[0] + '.png'
  skimage.io.imsave(output_img, texture)

  # mtl file
  of = open(output_mtl, 'w')
  print("newmtl material0", file=of)
  print("Ka %f %f %f" % (1.0, 1.0, 1.0), file=of)
  print("Kd %f %f %f" % (1.0, 1.0, 1.0), file=of)
  print("Ks %f %f %f" % (0.0, 0.0, 0.0), file=of)
  print("map_Kd", output_img, file=of)
  of.close()

def get_boilerplate_json(output_img, output_00t):
  return {
    "properties": 
    {
     "bounding_level": 0.0,
     "highlight_col": 65535,
     "image": output_img,
     "image_col": 16777215,
     "scale": 1000.0,
     "sharp_pixels": 1,
     "triangulation": output_00t,
     "tricol": 0,
     "undercol": 16777215,
     "use_bounding": 1,
     "use_specified": 0,
     "world_col": 16777215
    }
  }

def vulcan_register_image(output_00t, texture, xyz0, xyz1, output_path):
  import json
  output_img = os.path.splitext(output_path)[0] + '.png'

  spec_json = get_boilerplate_json(output_img, output_00t)
  skimage.io.imsave(output_img, texture)
  spec_json["points"] = []
  spec_json["points"].append({"image": [0,0,0],"world": xyz0})
  spec_json["points"].append({"image": [1,1,1],"world": xyz1})

  open(output_path, 'w').write(json.dumps(spec_json, sort_keys=True, indent=4).replace(': NaN', ' = u').replace('": ', '" = '))

# save a triangulation as a Vulcan IREG (ireg, 00t, png)
def vulcan_save_ireg(nodes, faces, texture, output_path, rows_cols = None):
  import json
  spec_json = get_boilerplate_json(output_img, output_00t)

  output_00t = os.path.splitext(output_path)[0] + '.00t'
  vulcan_save_tri(nodes, faces, output_00t)
  
  output_img = os.path.splitext(output_path)[0] + '.png'
  skimage.io.imsave(output_img, texture)

  # vt = [[0.0, 0.0], nodes[0].tolist(), [1.0, 1.0], nodes[-1].tolist()]

  if rows_cols is not None:
    vt = vulcan_texture_vt(*rows_cols)

    spec_json["points"] = [{"image": vt[i].tolist(),"world": nodes[i].tolist()} for i in range(len(vt))]
    #{"image": [0.0, 0.0],"world": nodes[0].tolist()}, {"image": [1.0, 1.0], "world": nodes[-1].tolist()}]


  open(output_path, 'w').write(json.dumps(spec_json, sort_keys=True, indent=4).replace(': NaN', ' = u').replace('": ', '" = '))