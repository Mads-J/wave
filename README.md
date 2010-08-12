# WaveConnect GIS Resources

This directory contains GIS resources assembled for the PG&E WaveConnect
resource assessment survey.  The files are formatted in such a way that they may
be viewed using the QGIS program and manipulated using the GDAL library. QGIS
and GDAL are described later on in this document.  The contents of this
directory are as follows:

## Files

  * *WaveConnect.qgs:* Main QGIS project file.

## Datasets
  
  * [Bathymetry/bathy](doc/Bathymetry_bathy.html) : Bathymetry data for the
    WaveConnect study area.
  * [Bathymetry/NWSSwanBathy](doc/Bathymetry_NWSSwanBathy.html) : Bathymetry data
    from the old NWS SWAN system.
  * [Bathymetry/bound](doc/Bathymetry_bound.html) : Vector outlines for some of
    bathymetry surveys listed above.
  * [NDBCbuoys](doc/NDBCbuoys.html) : Location of observation stations accessible
    through the NDBC system.
  * [NOAACharts](doc/NOAACharts.html) : Background imagry of NOAA nautical
    charts.

## QGIS

Quantum GIS (QGIS) is an open source Geospatial Information System (GIS) that
was chosen to support the WaveConnect project.  QGIS was chosen because it is
cost effective and meets developer requirements for support across a diverse
range of platforms.  The following webpages contain info relevant to obtaining
and using QGIS:

  * *The QGIS homepage:* [http://www.qgis.org/][1]
  * *The QGIS downloads page:*
    [http://www.qgis.org/en/download/current-software.html][2]
  * *Mac OS X binaries:* [http://www.kyngchaos.com/software:qgis][3] (The
    "standalone" Mac binaries are recommended as they require the installation
    of no additional components and are self-contained and easy to uninstall)

## GDAL

The Geospatial Data Abstraction Library (GDAL) is the standard open source tool
kit for manipulating and transcoding geospatial data.  The following tools
provided by the GDAL library were used extensively in the production of this
data:

  * `gdal_translate`: Used to translate raster data from proprietary formats,
    such as ArcGIS coverages, or esoteric formats such as NOAA BSB files to
    commonly used raster formats such as GeoTIFF.
  * `gdalwarp`: Used to reproject raster data from coordinate systems such as
    Universal Transverse Mercator (UTM) to the common EPSG:4326 Lat/Lon
    projection used throughout this project. `gdalwarp` was also used to merge
    or "mosaic" several raster datasets into one unified dataset.
  * `ogr2ogr`: Used to reproject and reformat vector data.

Information and source code for GDAL can be obtained from the following
webpages:

  * *The GDAL Homepage:* [http://www.gdal.org/][4]
  * *GDAL Binaries:* [http://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries][5]

  [1]: http://www.qgis.org/
  [2]: http://www.qgis.org/en/download/current-software.html
  [3]: http://www.kyngchaos.com/software:qgis
  [4]: http://www.gdal.org/
  [5]: http://trac.osgeo.org/gdal/wiki/DownloadingGdalBinaries