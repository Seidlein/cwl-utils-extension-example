# cwl-utils-extension-example



Output of python test script:


python run_cwl_trial.py

=== Step 6: Baseline check (no inspection) ===
valid_file passed baseline check (no inspection)
invalid_file passed baseline check (no inspection)

=== Step 7: Inspection enabled — valid GeoTIFF ===
Inspecting GeoTIFF: /Users/janlukasseidlein/Documents/cwl-utils/valid.tif
/Users/janlukasseidlein/Documents/cwl-utils/path/to/venv/lib/python3.14/site-packages/osgeo/gdal.py:606: FutureWarning: Neither gdal.UseExceptions() nor gdal.DontUseExceptions() has been explicitly called. In GDAL 4.0, exceptions will be enabled by default.
  warnings.warn(
valid_file passed inspection

=== Step 8: Inspection enabled — invalid GeoTIFF ===
Inspecting GeoTIFF: /Users/janlukasseidlein/Documents/cwl-utils/invalid.tif
ERROR 4: `/Users/janlukasseidlein/Documents/cwl-utils/invalid.tif' not recognized as being in a supported file format.
invalid_file correctly failed inspection:
  /Users/janlukasseidlein/Documents/cwl-utils/invalid.tif is not a readable GeoTIFF

=== Step 9: Guard checks ===
remote_file correctly ignored
missing_file correctly ignored

Trial complete.