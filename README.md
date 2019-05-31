# bm_tri_surface_color
Creates a georeferenced image with model block/voxel color along a surface. Also known as a Surface Map.    
Requires the Maptek Vulcan python module to run.  
Output is in Vulcan ireg proprietary format, which can then be coverted to a industry standard geotiff using a associated script.  
This is because the script which generates the ireg must be run in the vulcan python enviroment, which does does not contain the gdal python module by default.  
Once the ireg is generated, the converter script can be either run again in the same enviroment if the gdal module was manually deployed or in a anaconda/winpython enviroment which does not contain vulcan but will have the gdal module.  


## Generate ireg from vulcan data
![screenshot1](https://github.com/pemn/bm_tri_surface_color/blob/master/assets/screenshot1.png)

## Generate convert the vulcan ireg to a geotiff
![screenshot2](https://github.com/pemn/bm_tri_surface_color/blob/master/assets/screenshot2.png)

## Output Examples
![dump0000](https://github.com/pemn/bm_tri_surface_color/blob/master/assets/dump0000.png)  
![dump0001](https://github.com/pemn/bm_tri_surface_color/blob/master/assets/dump0001.png)

## License
Apache 2.0
