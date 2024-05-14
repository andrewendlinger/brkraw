from typing import Type
from .scan import Scan, Study, ScanInfo

ScanDataType = Type[Scan]
StudyDataType = Type[Study]
ScanInfoType = Type[ScanInfo]

__all__ = ['ScanDataType', 'StudyDataType', 'ScanInfoType']