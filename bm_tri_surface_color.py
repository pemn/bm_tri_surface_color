#!python
# Copyright 2019 Vale
# github.com/pemn/bm_tri_surface_color
# create a georeferenced image with block color along a surface
# input_tri: surface
# input_scd: legend file containing a block_color legend with same name as variable
# input_bmf: block model file
# input_var: block model variable with legend color
# output: vulcan ireg with georeferencing and a png with same name with the texture
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

from _gui import usage_gui, pd_get_dataframe, table_field, smartfilelist

from vulcan_mapfile import VulcanScd
from voxelschema import Voxelschema
from vulcan_save_tri import vulcan_register_image, gdal_save_geotiff

def bm_tri_surface_color(input_tri, input_scd, input_bmf, input_var, output):
  import vulcan
  scd = VulcanScd(input_scd, 'BLOCK_COLOUR', input_var)
  tri = vulcan.triangulation(input_tri)
  tri_extent = tri.extent()

  bm = vulcan.block_model(input_bmf)


  n_schema = bm.model_n_schemas()-1

  voxels = Voxelschema(bm.model_schema_size(n_schema), bm.model_schema_dimensions(n_schema))

  # to improve performance, preselect only blocks below or touching the surface
  bm.select(' -X -B "%s" -C "zworld - zlength * 0.5 ge %.2f' % (input_tri, tri_extent[0][2]))

  c = 0
  for block in bm:
    c+= 1
    if c % 1000 == 0:
      print(c,"blocks processed")
    xyzw = bm.get_multiple(['xworld', 'yworld', 'zworld'])
    xyzc = bm.get_multiple(['xcentre', 'ycentre', 'zcentre'])
    xyzl = bm.get_multiple(['xlength', 'ylength', 'zlength'])
    d = np.nan
    try:
      z = tri.get_elevation(xyzw[0], xyzw[1])
      if z > -9e+27:
        d = abs(z - xyzw[2])
    except:
      pass
    # print(xyzw, d)
    voxels.flag_by_block(xyzc, xyzl, d, 'min')

  print(c,"blocks processed")
  grid2d = voxels.get_2d_minmax('min')

  # on the texture, i is y and x is j
  texture = np.ndarray((grid2d.shape[1], grid2d.shape[0], 3))

  for i in range(voxels.shape[0]):
    for j in range(voxels.shape[1]):
      k = voxels.get_k_minmax(i, j, 'min')
      xyz = voxels.xyz([i,j,k])
      bm.find_xyz(*xyz)
      value_var = bm.get_string(input_var)
      value_rgb = scd[value_var]
      # y must be inverted to look the same way in 90o rotated models and on the image
      texture[texture.shape[0] - j - 1, i] = value_rgb

  xyz = []
  xyz.append(bm.to_world(*voxels.xyz([0,0,0])))
  xyz.append(bm.to_world(*voxels.xyz([voxels.shape[0],0,0])))
  xyz.append(bm.to_world(*voxels.xyz([voxels.shape[0],voxels.shape[1],0])))
  xyz.append(bm.to_world(*voxels.xyz([0,voxels.shape[1],0])))

  if output.endswith('ireg'):
    vulcan_register_image(input_tri, texture, xyz, output)
  else:
    gdal_save_geotiff(texture, xyz, output)


main = bm_tri_surface_color

if __name__=="__main__":
  usage_gui(__doc__)