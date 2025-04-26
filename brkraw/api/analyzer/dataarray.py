"""Data Array Analyzer Module.

This module is dedicated to the analysis of data arrays, focusing on extracting and structuring
data array information from raw datasets. It provides functionalities to interpret and convert
data arrays into more accessible formats, complementing the broader data processing framework.
"""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

import numpy as np

from .base import BaseAnalyzer

if TYPE_CHECKING:
    from brkraw.api.pvobj.types import PvFileBuffer

    from ..data import ScanInfo


class DataArrayAnalyzer(BaseAnalyzer):
    """Analyzes specific data array information and returns structured data arrays and related metadata.

    This analyzer takes raw data array inputs and processes them to extract significant array metadata,
    such as data type and shape, and prepares the data array for further analytical processing.

    Args:
        infoobj (ScanInfo): The information object containing metadata related to data arrays.
        fileobj (Union[BufferedReader, ZipExtFile]): The file object from which the data array is read.

    Attributes:
        slope (float): The scaling factor applied to the data array values.
        offset (float): The offset added to the data array values.
        dtype (type): The data type of the data array.
        shape (list[int]): The dimensions of the data array.
        shape_desc (list[str]): Descriptions of the data array dimensions.
    """

    def __init__(self, infoobj: "ScanInfo", fileobj: PvFileBuffer):
        """Initialize the DataArrayAnalyzer with an information object and a file object."""
        infoobj = copy(infoobj)
        self._parse_info(infoobj)
        self.buffer = fileobj

    def _parse_info(self, infoobj: "ScanInfo"):
        """Parse the information object to set the data array properties such as slope, offset, and data type."""
        if not hasattr(infoobj, "dataarray"):
            raise AttributeError
        self.slope = infoobj.dataarray["slope"]
        self.offset = infoobj.dataarray["offset"]
        self.dtype = infoobj.dataarray["dtype"]
        self.shape = infoobj.image["shape"][:]
        self.shape_desc = infoobj.image["dim_desc"][:]
        if infoobj.frame_group and infoobj.frame_group["type"]:
            self._calc_array_shape(infoobj)

    def _calc_array_shape(self, infoobj: "ScanInfo"):
        """Calculate and extend the shape and description of the data array based on frame group information."""
        self.shape.extend(infoobj.frame_group["shape"][:])
        self.shape_desc.extend(
            [fgid.replace("FG_", "").lower() for fgid in infoobj.frame_group["id"]]
        )

    def get_dataarray(self):
        """Read and return the structured data array from the buffer, applying data type and shape transformations."""
        self.buffer.seek(0)
        arr = np.frombuffer(self.buffer.read(), self.dtype)

        print("chosen read in dataype:", self.dtype)
        print("input array size:", arr.size)
        print("input array shape:", arr.shape, "-->", np.prod(arr.shape))
        print("(meta)data array shape", self.shape, "-->", np.prod(self.shape))
        print(
            "potential complex shape:",
            self.shape + [2],
            "-->",
            np.prod(self.shape + [2]),
        )
        print("")
        print("arr.size == np.prod(self.shape)", arr.size == np.prod(self.shape))
        print(
            "arr.size == np.prod(self.shape + [2])",
            arr.size == np.prod(self.shape + [2]),
        )

        # Check if reshape is possible for the original shape
        if arr.size == np.prod(self.shape):
            arr_out = arr.reshape(self.shape, order="F")

        elif arr.size == np.prod(self.shape + [2]):
            # Reshape with complex format (adding 2 elements per entry)
            N_mid = len(arr) // 2

            # Split the array into real and imaginary parts
            real_part = arr[:N_mid]
            imag_part = arr[N_mid:]

            # Combine them into a complex array
            complex_arr = real_part + 1j * imag_part
            arr_out = complex_arr.reshape(self.shape, order="F")

        else:
            # raise ValueError
            print(
                f"Unresolvable shape mismatch: "
                f"Array size ({arr.size}) does not match the target shape ({self.shape}), "
                f"and reshaping with complex format also fails."
            )

            return arr

        return arr_out
