#!python
# Copyright 2019 Vale
# create a tiff with legend color along a surface
# input_tri: surface
# input_scd: legend file containing a block_color legend with same name as variable
# input_bmf: block model file
# input_var: block model variable with legend color
# output: tiff file with colors
# v1.0 05/2019 paulo.ernesto
'''
usage: $0 input_tri*00t input_scd*scd input_bmf*bmf input_var:input_bmf output*ireg
'''
import sys
import pandas as pd
import numpy as np
import math
import skimage.io
from _gui import usage_gui, pd_get_dataframe, table_field, smartfilelist

from vulcan_mapfile import VulcanScd
from voxelschema import Voxelschema
from vulcan_save_tri import vulcan_register_image


def bm_tri_surface_color(input_tri, input_scd, input_bmf, input_var, output):
  import vulcan
  scd = VulcanScd(input_scd, 'BLOCK_COLOUR', input_var)

  bm = vulcan.block_model(input_bmf)


  n_schema = bm.model_n_schemas()-1
  tri = vulcan.triangulation(input_tri)

  voxels = Voxelschema(bm.model_schema_size(n_schema), bm.model_schema_dimensions(n_schema))
  # voxels.mask = False
  # voxels.fill(0)
  # print(voxels)
  # voxels.flag_by_block([500, 500, 500], [1000, 1000, 1000], 999)

  for block in bm:
    xyzw = bm.get_multiple(['xworld', 'yworld', 'zworld'])
    xyzc = bm.get_multiple(['xcentre', 'ycentre', 'zcentre'])
    xyzl = bm.get_multiple(['xlength', 'ylength', 'zlength'])
    # print(xyzw)
    # print(xyzc)
    # print(xyzl)
    z = tri.get_elevation(xyzw[0], xyzw[1])
    # print(z)
    voxels.flag_by_block(xyzc, xyzl, abs(z - xyzw[2]), 'min')


  grid2d = voxels.get_2d_minmax('min')

  # texture = np.ndarray((grid2d.shape[0], grid2d.shape[1], 3), dtype=np.uint8)
  texture = np.ndarray((grid2d.shape[0], grid2d.shape[1], 3))

  for i in range(voxels.shape[0]):
    for j in range(voxels.shape[1]):
      k = voxels.get_k_minmax(i, j, 'min')
      xyz = voxels.xyz([i,j,k])
      bm.find_xyz(*xyz)
      value_var = bm.get_string(input_var)
      value_rgb = scd[value_var]
      # print("%d,%d = %s,%s"  % (i,j,value_var, value_rgb))
      texture[i,j] = value_rgb


    # texture[i, j, k] = rgb[k]

  # skimage.io.imsave(output, texture)
  xyz0 = bm.to_world(*voxels.xyz([0,0,0]))
  xyz1 = bm.to_world(*voxels.xyz(voxels.shape))

  vulcan_register_image(input_tri, texture, xyz0, xyz1, output)
  # voxels.save_2d_grid('output2d.csv', grid2d)
  # print(voxels.ijk([1000, 1000, 1000]))
  # voxels.save_grid('output.csv')


main = bm_tri_surface_color

if __name__=="__main__":
  usage_gui(__doc__)
