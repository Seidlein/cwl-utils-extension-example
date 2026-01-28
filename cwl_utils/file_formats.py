# SPDX-License-Identifier: Apache-2.0
"""
CWL file formats utilities with strict GeoTIFF inspection.

For more information, please visit https://www.commonwl.org/user_guide/16-file-formats/
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

from rdflib import OWL, RDFS, Graph, URIRef
from schema_salad.exceptions import ValidationException
from schema_salad.utils import aslist, json_dumps

from cwl_utils.types import CWLFileType

GEOTIFF_URI = "http://edamontology.org/format_3590"


def formatSubclassOf(fmt: str, cls: str, ontology: Graph | None, visited: set[str]) -> bool:
    """Determine if `fmt` is a subclass of `cls`."""
    if URIRef(fmt) == URIRef(cls):
        return True
    if ontology is None:
        return False
    if fmt in visited:
        return False
    visited.add(fmt)
    uriRefFmt = URIRef(fmt)

    for _s, _p, o in ontology.triples((uriRefFmt, RDFS.subClassOf, None)):
        if formatSubclassOf(o, cls, ontology, visited):
            return True
    for _s, _p, o in ontology.triples((uriRefFmt, OWL.equivalentClass, None)):
        if formatSubclassOf(o, cls, ontology, visited):
            return True
    for s, _p, _o in ontology.triples((None, OWL.equivalentClass, uriRefFmt)):
        if formatSubclassOf(s, cls, ontology, visited):
            return True
    return False


def _local_file_path(afile: CWLFileType) -> str | None:
    """Return a local filesystem path if it's a file:// URI and exists on disk."""
    location = afile.get("location")
    if not isinstance(location, str) or not location.startswith("file://"):
        return None
    path = urlparse(location).path
    if not path or not os.path.exists(path):
        return None
    return path


def _is_geotiff_format(fmt: str, ontology: Graph | None) -> bool:
    """Return True if fmt is GeoTIFF or a subclass thereof."""
    return formatSubclassOf(fmt, GEOTIFF_URI, ontology, set())


def _inspect_geotiff(path: str) -> None:
    """Perform strict byte-level GeoTIFF inspection using GDAL."""
    print("Inspecting GeoTIFF:", path)
    try:
        from osgeo import gdal
    except Exception:
        raise RuntimeError("GDAL Python bindings required for GeoTIFF inspection")

    ds = gdal.Open(path, gdal.GA_ReadOnly)
    if ds is None:
        raise ValidationException(f"{path} is not a readable GeoTIFF")

    driver = ds.GetDriver()
    if driver is None or driver.ShortName != "GTiff":
        raise ValidationException(f"{path} is not a GTiff dataset")

    proj = ds.GetProjection()
    if not proj or proj.strip() == "":
        raise ValidationException(f"{path} lacks spatial reference")

    # Optional: check raster dimensions and bands
    if ds.RasterCount < 1:
        raise ValidationException(f"{path} has no raster bands")

    ds = None


def check_format(
    actual_file: CWLFileType | list[CWLFileType],
    input_formats: list[str] | str,
    ontology: Graph | None,
    inspect_files: bool = False,
) -> None:
    """
    Confirm that the format present is valid for the allowed formats.

    If inspect_files=True, perform byte-level inspection for GeoTIFFs:
      - only local file:// URIs
      - must exist on disk
      - raises ValidationException for invalid files
    """
    for afile in aslist(actual_file):
        if not afile:
            continue

        if "format" not in afile:
            raise ValidationException(f"File has no 'format' defined: {json_dumps(afile, indent=4)}")

        # Check format matches allowed ontology
        matched = False
        for inpf in aslist(input_formats):
            if afile["format"] == inpf or formatSubclassOf(afile["format"], inpf, ontology, set()):
                matched = True
                break
        if not matched:
            raise ValidationException(f"File has an incompatible format: {json_dumps(afile, indent=4)}")

        # Optional byte-level inspection
        if inspect_files:
            path = _local_file_path(afile)
            if path and _is_geotiff_format(afile["format"], ontology):
                _inspect_geotiff(path)