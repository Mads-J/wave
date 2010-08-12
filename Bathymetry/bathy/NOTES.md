# Bathymetry data for WaveConnect Project

## Included Files

  * **bathyStyle.qml**

    QGIS style file containing formatting rules that can be used to bestow a uniform
    grayscale look on shallow bathymetry data so that it may be compared visually.
    Depth range is set at -60 to 0 meters.

***

  * **northBayBathy.tif**
  * **southBayBathy.tif**

    High resolution DEMs of the navigable channels of north and south Humboldt Bay.

    **Original Resolution:** 1 m

    **Original File Format:** ArcGIS Binary Raster

    **Original Projection:** UTM Zone 10, WGS84 Ellipsoid, WGS84 Datum (EPSG:32610) 

    **Survey Date:** 2005

    **Source:** [http://seafloor.csumb.edu/csmp/csmp_datacatalog.html][1]

***

  * **southShoreBathy.tif **
  * **northShoreBathy1.tif **
  * **northShoreBathy2.tif **

    High resolution DEMs taken ~ 500 meters off shore of the Humboldt Bay coast.
    These DEMs cover the WaveConnect project area.

    **Original Resolution:** 2 m

    **Original File Format:** ArcGIS Binary Raster

    **Original Projection:** UTM Zone 10, GRS80 Ellipsoid, NAD83 Datum (EPSG:26910) 

    **Survey Date:** 2009

    **Source:** [http://seafloor.csumb.edu/csmp/csmp_datacatalog.html][1]

***

  * **northCoast.tif **

    3 arc second DEM from the National Geophysical Data Center (GEODAS) Coastal
    Relief Model.  Covers a wide area of the north coast.

    **Original Resolution:** 3 seconds of arc

    **Original File Format:** ArcGIS Binary Raster

    **Original Projection:** Unspecified Lat/Lon  (Possibly EPSG:4326?) 

    **Survey Date:** Various

    **Source:** [http://seafloor.csumb.edu/csmp/csmp_datacatalog.html][1]

# Raster File Processing

Reprojected to EPSG:4326 Lat/Lon coordinate system using:

    gdalwarp -t_srs EPSG:4326 -of Gtiff hdr.adf [output].tif

Transcribed to NetCDF format using:

    gdal_translate -of netCDF [input].tif [output].nc

  [1]: http://seafloor.csumb.edu/csmp/csmp_datacatalog.html (California Seafloor Mapping Project) 
  [2]: http://www.ngdc.noaa.gov/mgg/coastal/crm.html (GEODAS Coastal Relief Model)