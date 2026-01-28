#!/usr/bin/env python3
"""
Full CWL-utils GeoTIFF trial (Steps 3–9).

- Step 3: Construct minimal ontology graph
- Step 4: Prepare CWL File objects
- Step 5: Import check_format
- Step 6: Baseline check (no inspection)
- Step 7: Enable inspection — valid GeoTIFF
- Step 8: Enable inspection — invalid GeoTIFF
- Step 9: Verify guards (remote file and missing file)
"""

from pathlib import Path
from rdflib import Graph, URIRef, RDFS
from schema_salad.exceptions import ValidationException

# --- Step 3: Construct minimal ontology graph ---
GEOTIFF = "http://edamontology.org/format_3590"
TIFF = "http://edamontology.org/format_3464"
g = Graph()
g.add((URIRef(GEOTIFF), RDFS.subClassOf, URIRef(TIFF)))

# --- Step 4: Prepare CWL File objects ---
def file_uri(p: Path) -> str:
    return f"file://{p.absolute()}"

valid_path = Path("valid.tif").absolute()
invalid_path = Path("invalid.tif").absolute()

valid_file = {"class": "File", "location": file_uri(valid_path), "format": GEOTIFF}
invalid_file = {"class": "File", "location": file_uri(invalid_path), "format": GEOTIFF}

# --- Step 5: Import check_format ---
from cwl_utils.file_formats import check_format

print("=== Step 6: Baseline check (no inspection) ===")
for f, name in [(valid_file, "valid_file"), (invalid_file, "invalid_file")]:
    try:
        check_format(f, GEOTIFF, g)
        print(f"{name} passed baseline check (no inspection)")
    except ValidationException as e:
        print(f"{name} FAILED baseline check: {e}")

print("\n=== Step 7: Inspection enabled — valid GeoTIFF ===")
try:
    check_format(valid_file, GEOTIFF, g, inspect_files=True)
    print("valid_file passed inspection")
except ValidationException as e:
    print(f"valid_file FAILED inspection: {e}")

print("\n=== Step 8: Inspection enabled — invalid GeoTIFF ===")
try:
    check_format(invalid_file, GEOTIFF, g, inspect_files=True)
    print("invalid_file passed inspection (unexpected!)")
except ValidationException as e:
    print(f"invalid_file correctly failed inspection:\n  {e}")

print("\n=== Step 9: Guard checks ===")
# Remote file should be ignored
remote_file = {"class": "File", "location": "https://example.org/data.tif", "format": GEOTIFF}
try:
    check_format(remote_file, GEOTIFF, g, inspect_files=True)
    print("remote_file correctly ignored")
except ValidationException as e:
    print(f"remote_file FAILED (unexpected): {e}")

# Missing local file should be ignored
missing_file = {"class": "File", "location": file_uri(Path("does_not_exist.tif")), "format": GEOTIFF}
try:
    check_format(missing_file, GEOTIFF, g, inspect_files=True)
    print("missing_file correctly ignored")
except ValidationException as e:
    print(f"missing_file FAILED (unexpected): {e}")

print("\nTrial complete.")