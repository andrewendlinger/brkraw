from typing import Type
from .scan import Scan, ScanInfo
from .study import Study

ScanDataType = Type[Scan]
StudyDataType = Type[Study]
ScanInfoType = Type[ScanInfo]

__all__ = ['ScanDataType', 'StudyDataType', 'ScanInfoType']