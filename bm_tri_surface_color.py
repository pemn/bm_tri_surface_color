#!python
# create a georeferenced image with colors by block values over a surface
# Copyright 2019 Vale
# github.com/pemn/bm_tri_surface_color
# input_tri: surface in vulcan 00t format
# input_scd: (optional) a vulcan scd containing a legend with same name as grade variable and a color palete
# input_bmf: vulcan block model file
# input_var: block model variable to be used as grade if required
# mode: 
# ~ near = color by grade of nearest surface block
# ~ grid_xxx = color by the chosen agregation of all blocks below surface
# output_path: csv with raw data or geotiff/ireg with georeferencing (geotiff requires gdal module)
# geotiff_epsg: (optional, geotiff only) spatial reference system for geotiff
# v1.1 09/2019 paulo.ernesto
# v1.0 05/2019 paulo.ernesto
'''
usage: $0 input_tri*00t input_scd*scd input_bmf*bmf input_var:input_bmf mode%near,major,mean,sum output_path*ireg,csv,tiff geotiff_epsg=29193
'''
import sys, os

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, pd_save_dataframe, pyd_zip_extract
pyd_zip_extract()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from vulcan_mapfile import VulcanScd
from voxelbase import VoxelBase
from vulcan_save_tri import vulcan_register_image, gdal_save_geotiff

def bm_detect_density(bm):
  for v in bm.field_list_numbers():
    if v.startswith('dens'):
      return v
  return 'density'

def pd_tri_intersections(tri, bm, input_var, ax, ay, xyz0, xyz1):
  bdfa = []
  xyzi = tri.segment_intersections(*xyz0, *xyz1)
  if len(xyzi):
    for xyzw in xyzi:
      if bm.find_world_xyz(*xyzw):
        print("block not found: ij", ax ,ay ,"xyz" ,*xyzw)
        continue
      value_var = bm.get_string(input_var)
      #value_rgba = scd.get_rgb(value_var, True)
      bdfa.append(xyzw + [ax, ay, value_var])

  return pd.DataFrame(bdfa, columns=['x','y','z','i','j',input_var])

def var_breakdown(df, var, mode):
  v = None
  if mode == 'mean':
    v = df[var].nanmean()
  if mode == 'sum':
    v = df[var].nansum()
  else:
    v = df[var].value_counts().argmax()
  return v

def pd_bm_column(voxels, bm, input_var, axyz, ax, ay):
  # [i,j,0]
  aijk = [0,0,0]
  aijk[axyz[0]] = ax
  aijk[axyz[1]] = ay
  #box0, box1 = voxels.bb(aijk)
  box0 = voxels.xyz(aijk, 'bb0')
  aijk[axyz[2]] = voxels.shape[axyz[2]]
  box1 = voxels.xyz(aijk, 'bb1')
  bsbb = np.empty(len(box0) + len(box1))
  bsbb[0::2] = box0
  bsbb[1::2] = box1
  bs = ' -bm %.2f %.2f %.2f %.2f %.2f %.2f' % tuple(bsbb)
  idf = bm.get_pandas([input_var], bs)
  idf.mask(idf == -99, inplace=True)
  return idf

def find_near_row(df, tri):
  row_near = None
  # early exit for single block special case
  if len(df):
    d_min = None
    for ri,rd in df.iterrows():
      z = None
      try:
        z = tri.get_elevation(*rd['x','y'])
        if z == -9e+27:
          z = None
      except:
        pass
      # region outside triangulation?
      if z is None:
        continue
      d = abs(z - rd['z'])
      if d_min is None or d < d_min:
        d_min = d
        row_near = rd
    else:
      if row_near is None:
        row_near = rd

  return row_near

class AUTOCMAP(dict):
  def __call__(self, arr):
    plt.set_cmap('Spectral')
    cmap = plt.get_cmap()
    text_mode = False
    for k,v in self.items():
      if type(v) == str:
        text_mode = True
        break
    if text_mode:
      s = set(self.values())
      c,l = pd.factorize(tuple(self.values()))
      #return cmap(c / len(c))
      n = 0
      for k,v in self.items():
        arr[k] = np.multiply(cmap(c[n] / (len(l) - 1)), 255)
        n += 1
    else:
      v0 = min(self.values())
      v1 = max(self.values())
      if v1 == 0:
        v1 = 1
      #return cmap((arr - v0) / v1)
      for k,v in self.items():
        arr[k] = np.multiply(cmap((v - v0) / v1), 255)



def bm_tri_surface_color(input_tri, input_scd, input_bmf, input_var, mode, output_path, geotiff_epsg):
  import vulcan
  scd = None
  rgb = None
  if input_scd and os.path.exists(input_scd):
    scd = VulcanScd(input_scd, 'BLOCK_COLOUR', input_var)

    if scd.palete_missing():
      raise Exception("scd does not have a palete (DEVICE_COLOR)")
    
    if scd.legend_missing():
      raise Exception("scd does not have a legend for variable: " + input_var)
  else:
    rgb = AUTOCMAP()

  bm = vulcan.block_model(input_bmf)

  voxels = VoxelBase.from_bmf(bm)

  # on the texture, i is y and x is j
  #, dtype=np.uint8
  #texture = np.ma.MaskedArray(np.zeros((voxels.shape[1], voxels.shape[0], 3)), np.ones(voxels.shape[1] * voxels.shape[0] * 3, np.bool_))
  # csv buffer
  odf = pd.DataFrame()

  tri = vulcan.triangulation(input_tri)
  t0, t1 = tri.extent()
  t0 = np.add(voxels.ijk(t0), -1)
  t1 = np.add(voxels.ijk(t1), 1)
  c = 0
  # static axis "Z"
  az = 2
  axyz = [0,1,2]
  # TODO: fix this so it works on other axis, right now its broken
  #for i in axyz:
  #  if abs(t1[i] - t0[i]) < abs(t1[az] - t0[az]):
  #    az = i
  #int(np.argmin(np.subtract(t1,t0)))
  # send static axis to end of list
  #axyz.remove(az)
  #axyz.append(az)
  axyz = tuple(axyz)

  n = (t1[axyz[0]] - t0[axyz[0]] - 1) * (t1[axyz[1]] - t0[axyz[1]] - 1)
  print(t1[axyz[0]] - t0[axyz[0]], t1[axyz[1]] - t0[axyz[1]])
  texture = np.zeros((voxels.shape[axyz[1]], voxels.shape[axyz[0]], 4), dtype='uint8')
  for ax in range(0, voxels.shape[axyz[0]]):
    for ay in range(0, voxels.shape[axyz[1]]):
      if c % 1000 == 0: 
        print("%6d / %6d blocks processed" % (c, n))
      c += 1
      ijk0 = [None, None, None]
      ijk1 = [None, None, None]
      ijk0[axyz[0]] = ijk1[axyz[0]] = ax
      ijk0[axyz[1]] = ijk1[axyz[1]] = ay
      ijk0[axyz[2]] = t0[axyz[2]]
      ijk1[axyz[2]] = t1[axyz[2]]

      xyz0 = voxels.xyz(ijk0)
      xyz1 = voxels.xyz(ijk1)

      # we can use get_z in horizontal surfaces
      bdf = None
      v = None
      if mode == 'near':
        bdf = pd_tri_intersections(tri, bm, input_var, ax, ay, xyz0, xyz1)
        row = find_near_row(bdf, tri)
        if row is not None:
          v = row[input_var]
        
        #v = bdf.loc[row, ['r','g','b','a']]
      else:
        bdf = pd_bm_column(voxels, bm, input_var, axyz, ax, ay)
        v = var_breakdown(bdf, input_var, mode)
        xyz = np.mean(np.stack([xyz0, xyz1]), 0)
        #bdf[['x','y','z']] = xyz
        bdf['x'] = xyz[0]
        bdf['y'] = xyz[1]
        bdf['z'] = xyz[2]
        #v = scd.get_rgb(value_var, True)

      # y must be inverted to look the same way in 90° rotated models and on the image
      #texture[texture.shape[0] - ay - 1, ax] = v
      if scd:
        texture[texture.shape[0] - ay - 1, ax] = np.multiply(scd.get_rgb(v, True), 255)
      else:
        rgb[(texture.shape[0] - ay - 1, ax)] = v
      #scd.get_rgb(bdf.loc[row, input_var], True)

      #odf = odf.append(bdf)

  if not scd:
    print("not scd")
    rgb(texture)


  print(c, '/', n, 'blocks processed')

  ijk = np.zeros((4,3))
  ijk[2,axyz[0]] = ijk[1,axyz[0]] = voxels.shape[axyz[0]]
  ijk[3,axyz[1]] = ijk[2,axyz[1]] = voxels.shape[axyz[1]]

  xyz = voxels.xyz(ijk, 'box0')
  
  if output_path.lower().endswith('ireg'):
    vulcan_register_image(input_tri, texture, xyz.tolist(), output_path)
  elif output_path.lower().endswith('tiff'):
    gdal_save_geotiff(np.rollaxis(texture, 2), xyz, output_path, int(geotiff_epsg))
  else:
    pd_save_dataframe(odf, output_path)

main = bm_tri_surface_color

if __name__=="__main__":
  usage_gui(__doc__)

