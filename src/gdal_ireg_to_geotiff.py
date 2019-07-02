#!python
# Copyright 2019 Vale
# convert a vulcan ireg to a geotiff
# v1.0 05/2019 paulo.ernesto
'''
usage: $0 input_ireg*ireg output_tiff*tif,tiff,gtif,gtiff
'''
import sys, os
import numpy as np

# import modules from a pyz (zip) file with same name as scripts
sys.path.append(os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui

from vulcan_save_tri import gdal_save_geotiff

def gdal_ireg_to_geotiff(input_ireg, output_tiff):
  import json
  import gdal
  ireg_s = open(input_ireg).read()

  ireg_o = json.loads(ireg_s.replace(' = u', ': NaN').replace('" = ', '": '))

  source = gdal.Open(ireg_o['properties']['image'])
  rgb_array = source.ReadAsArray()

  gcps = [gcp['world'] + [gcp['image'][0] * rgb_array.shape[2], gcp['image'][1] * rgb_array.shape[1]] for gcp in ireg_o['points']]
  gdal_save_geotiff(rgb_array, gcps, output_tiff)

main = gdal_ireg_to_geotiff

if __name__=="__main__":
  usage_gui(__doc__)
