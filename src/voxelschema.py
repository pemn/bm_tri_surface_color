#!python
# voxelscheme
# v1.0 05/2019 paulo.ernesto

import numpy as np
import csv


# normalized voxel cube around all xyz points of a csv file
class Voxelschema(np.ma.MaskedArray):
  def __new__(cls, size, dimensions):
    if len(size) > 3:
      size = size[0:3]
    self = super().__new__(cls, np.ndarray(dimensions), np.ones(np.prod(dimensions), np.bool_))
    self._bl = np.array(size)
    self._o0 = np.zeros(3);
    return(self)

  # return the ijk of a voxel using our fixed voxel size instead of the voxel own size
  def ijk(self, xyz):
    #(block_centre, block_length) = Voxel.block(self._data.ix[c])
    #return tuple(int((xyz[i] - self._o0[i]) // self._bl[i]) for i in range(3))
    return np.divide(np.subtract(xyz, self._o0), self._bl).astype(np.int_)

  def xyz(self, ijk):
    return np.add(np.multiply(ijk, self._bl), self._o0)

  def block_extent(self, xyzc, xyzl):
    xyzr = np.multiply(xyzl, 0.5)
    return np.subtract(xyzc, xyzr), np.add(xyzc, xyzr)

  def flag_by_block(self, xyzc, xyzl, value, mode = 'first'):
    xyz0, xyz1 = self.block_extent(xyzc, xyzl)
    return self.flag_by_extent(xyz0, xyz1, value, mode)

  # flag grid cells that are touched by a block
  # in the case of multiple blocks touching a cell
  # use the block which intersects with the greater volume
  # input: block corners
  def flag_by_extent(self, xyz0, xyz1, value, mode = 'first'):
    ijk0 = self.ijk(xyz0)
    ijk1 = self.ijk(xyz1)
    # ijkd = np.subtract(ijk1, ijk0, dtype=np.int_, casting='unsafe')
    ijkd = np.subtract(ijk1, ijk0)
    for i in range(ijk0[0], ijk0[0] + ijkd[0]):
      for j in range(ijk0[1], ijk0[1] + ijkd[1]):
        for k in range(ijk0[2], ijk0[2] + ijkd[2]):
          if self[i,j,k] is np.ma.masked:
            pass
          elif mode == 'max' and self[i,j,k] < value:
            pass
          elif mode == 'min' and self[i,j,k] > value:
            pass
          else:
            continue

          self[i,j,k] = value

    return self

  def get_k_minmax(self, i, j, mode = 'max'):
    k = 0
    ks = self[i, j, :]
    if mode == 'max':
      k = ks.argmax()
    else:
      k = ks.argmin()
    return k

  def get_2d_minmax(self, mode = 'max'):
    grid = np.ma.MaskedArray(np.ndarray(self.shape[0:2]), np.ones(np.prod(self.shape[0:2]), np.bool_))
    for i in range(self.shape[0]):
      for j in range(self.shape[1]):
        k = self.get_k_minmax(i, j, mode)
        grid[i,j] = k

    return grid

  def save_2d_grid(self, path, grid):

    with open(path, 'w', newline='') as csvfile:
      csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
      csvwriter.writerow(['i', 'j','value'])
      for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
          csvwriter.writerow([i, j, grid[i,j]])

  def save_grid(self, path):
    with open(path, 'w', newline='') as csvfile:
      csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
      csvwriter.writerow(['i', 'j', 'k','value'])
      for i in range(self.shape[0]):
        for j in range(self.shape[1]):
          for k in range(self.shape[2]):
            csvwriter.writerow([i, j, k, self[i,j,k]])
