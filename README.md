## 📌 Description
Creates a georeferenced image with model block/voxel color along a surface. Also known as a Surface Map.    
Requires the Maptek Vulcan python module to run.  
Output is in Vulcan ireg proprietary format, which can then be coverted to a industry standard geotiff using a associated script.  
This is because the script which generates the ireg must be run in the vulcan python enviroment, which does does not contain the gdal python module by default.  
Once the ireg is generated, the converter script can be either run again in the same enviroment if the gdal module was manually deployed or in a anaconda/winpython enviroment which does not contain vulcan but will have the gdal module.  
## 📝 Parameters
name|optional|description
---|---|------
input_tri|❎|surface in vulcan 00t format
input_scd|☑️|a vulcan scd containing a legend with same name as grade variable and a color palete
input_bmf|❎|vulcan block model file
input_var|❎|block model variable to be used as grade if required
mode|near|use block nearest the surface
||major|use the most common value out of all blocks below surface
||mean|if the variable is numeric, use the mean of values of all blocks below surface
||sum|sum of values of all blocks below surface
output_path|❎|path to save result in one of the supported file formats
geotiff_epsg|☑️|Epsg code for geotiff coordinate reference system

## 📸 Screenshots
### graphic interface
![screenshot2](./assets/screenshot2.png?raw=true)

### Convert the vulcan ireg to a geotiff
![screenshot1](./assets/screenshot1.png?raw=true)

### Output Examples
![dump0000](./assets/dump0000.png?raw=true)  
![dump0001](./assets/dump0001.png?raw=true)
![dump0002](./assets/dump0002.png?raw=true)
## 🧩 Compatibility
distribution|status
---|---
![winpython_icon](https://github.com/pemn/assets/blob/main/winpython_icon.png?raw=true)|❌
![vulcan_icon](https://github.com/pemn/assets/blob/main/vulcan_icon.png?raw=true)|✔
![anaconda_icon](https://github.com/pemn/assets/blob/main/anaconda_icon.png?raw=true)|❌
## 🙋 Support
Any question or problem contact:
 - paulo.ernesto
## 💎 License
Apache 2.0
