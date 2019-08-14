#!python
# Copyright 2019 Vale
# github.com/pemn/bm_tri_surface_color
# create a georeferenced image (geotiff) with block color over a surface
# input_tri: surface in vulcan 00t format
# input_scd: a vulcan scd containing a legend with same name as variable and a color palete
# input_bmf: block model file
# input_var: block model variable with legend color
# output: geotiff or vulcan ireg with georeferencing (geotiff requires gdal module)
# v1.0 05/2019 paulo.ernesto
'''
usage: $0 input_tri*00t input_scd*scd input_bmf*bmf input_var:input_bmf output*ireg
'''
import sys, os
import pandas as pd
import numpy as np
import math
import skimage.io

# import modules from a pyz (zip) file with same name as scripts
sys.path.append(os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, pd_get_dataframe

from vulcan_mapfile import VulcanScd
from voxelbase import VoxelBase
from vulcan_save_tri import vulcan_register_image, gdal_save_geotiff

def bm_tri_surface_color(input_tri, input_scd, input_bmf, input_var, output):
  import vulcan
  scd = VulcanScd(input_scd, 'BLOCK_COLOUR', input_var)

  if scd.palete_missing():
    raise Exception("scd does not have a palete (DEVICE_COLOR)")
  
  if scd.legend_missing():
    raise Exception("scd does not have a legend for variable", input_var)

  bm = vulcan.block_model(input_bmf)

  voxels = VoxelBase.from_bmf(bm)

  # on the texture, i is y and x is j
  texture = np.ndarray((voxels.shape[1], voxels.shape[0], 3))

  tri = vulcan.triangulation(input_tri)
  tri_extent = tri.extent()

  for i in range(voxels.shape[0]):
    for j in range(voxels.shape[1]):
      xyzc = voxels.xyz([i,j,0])
      xyzw = bm.to_world(*xyzc)

      z = None
      try:
        z = tri.get_elevation(xyzw[0], xyzw[1])
        if z == -9e+27:
          z = None
      except:
        pass
      # region outside triangulation?
      if z is None:
        continue

      xyzw[2] = z

      if bm.find_world_xyz(*xyzw):
        print("block not found: ij",i,j,"xyz",*xyzw)
      else:
        value_var = bm.get_string(input_var)
        value_rgb = scd[value_var]
        # y must be inverted to look the same way in 90o rotated models and on the image
        texture[texture.shape[0] - j - 1, i] = value_rgb

  xyz = []
  xyz.append(bm.to_world(*voxels.xyz([0,0,0], 'box0')))
  xyz.append(bm.to_world(*voxels.xyz([voxels.shape[0],0,0], 'box0')))
  xyz.append(bm.to_world(*voxels.xyz([voxels.shape[0],voxels.shape[1],0], 'box0')))
  xyz.append(bm.to_world(*voxels.xyz([0,voxels.shape[1],0], 'box0')))

  if output.endswith('ireg'):
    vulcan_register_image(input_tri, texture, xyz, output)
  else:
    gdal_save_geotiff(texture, xyz, output)


main = bm_tri_surface_color

if __name__=="__main__":
  usage_gui(__doc__)
