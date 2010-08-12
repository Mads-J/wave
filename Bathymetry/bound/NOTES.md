# Bathymetry outlines for WaveConnect Project

## Included Files

  * **boundStyle.qml**

    QGIS style file containing formatting rules that can be used to bestow a uniform
    look on boundary files.  Each file describes a polygon and this style sets fill
    colors to be transparent and outlines to be thin and red.

***

  * **northBayBound.kml**
  * **northShoreBound1.kml**
  * **northShoreBound2.kml**
  * **southBayBound.kml**
  * **southShoreBound.kml**

    Polygon outlines of bathymetry DEMS obtained from the California Seafloor
    Mapping project.  Data originally provided as shapefiles obtained from:

    [http://seafloor.csumb.edu/csmp/csmp_datacatalog.html][1]


# Vector File Processing

Transcribed to KML format using:

    ogr2ogr -of KML [input].shp [output].kml

  [1]: http://seafloor.csumb.edu/csmp/csmp_datacatalog.html (California Seafloor Mapping Project) 