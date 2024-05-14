"""This module provides classes and functions for managing and analyzing MRI study data.

The primary class, Study, extends the functionalities of PvStudy from the brkraw.api.pvobj module
and integrates additional analysis capabilities through the BaseAnalyzer class. It handles the
processing of study-specific data, including the retrieval and management of scan objects,
parsing of study header information, and compiling comprehensive information about studies.

Classes:
    Study: Manages MRI study operations and integrates data processing and analysis capabilities.
           It provides methods to retrieve specific scans, parse and access study header data,
           and compile detailed information about the study and its associated scans and reconstructions.

Dependencies:
    PvStudy (from brkraw.api.pvobj): 
        Base class for handling the basic operations related to photovoltaic studies.
    BaseAnalyzer (from brkraw.api.analyzer.base): 
        Base class providing analytical methods used across different types of data analyses.
    Scan (from .scan): 
        Class representing individual scans within a study, providing detailed data access and manipulation.
    RecipeParser (from reshipe): 
        Utility class used for applying specified recipes to data objects, enabling structured data extraction and analysis.

This module is utilized in MRI research environments where detailed and structured analysis of photovoltaic data is required.
"""

from __future__ import annotations
import re
import os
import yaml
import warnings
from copy import copy
from pathlib import Path
from collections import OrderedDict
from dataclasses import dataclass
from reshipe import RecipeParser
from .scan import Scan
from brkraw.api.pvobj import PvStudy
from brkraw.api.analyzer.base import BaseAnalyzer
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Literal, Union
    from typing import OrderedDict as OrderedDictType, List
    from brkraw.api.pvobj import Parameter


@dataclass
class StudyHeader:
    header: dict
    scans: dict
    
    
@dataclass
class ScanHeader:
    scan_id: int
    header: dict
    recos: list
    
    
@dataclass
class RecoHeader:
    reco_id: int
    header: dict
    

class Study(PvStudy, BaseAnalyzer):
    """Handles operations related to a specific study, integrating PvStudy and analytical capabilities.

    This class extends the functionalities of PvStudy to include detailed analyses
    and operations specific to the study being handled. It integrates with various 
    data processing and analysis methods defined in the base analyzer.

    Attributes:
        header (Optional[dict]): Parsed study header information.
    """
    _spec: Optional[dict] = None
    _info: Optional[StudyHeader] = None
    _streamed_info: Optional[OrderedDictType] = None
    header: Optional[OrderedDictType] = None
    study_ref: Optional[Parameter] = None
    
    def __init__(self, path: Path, spec_path: Union[Path, str, None] = None) -> None:
        """Initializes the Study object with a specified path.

        Args:
            path (Path): The file system path to the study data.
        """
        super().__init__(self._resolve(path))
        self._import_spec(spec_path=spec_path)
        
    def get_scan(self,
                 scan_id: int,
                 reco_id: Optional[int] = None,
                 debug: bool = False) -> 'Scan':
        """Retrieves a Scan object for a given scan ID with optional reconstruction ID.

        Args:
            scan_id (int): The unique identifier for the scan.
            reco_id (Optional[int]): The reconstruction identifier, defaults to None.
            debug (bool): Flag to enable debugging outputs, defaults to False.

        Returns:
            Scan: The Scan object corresponding to the specified scan_id and reco_id.
        """
        pvscan = super().get_scan(scan_id)
        return Scan(pvobj=pvscan,
                    reco_id=reco_id,
                    study_address=id(self),
                    debug=debug)
    
    def _fetch_study_ref(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for scan_id in self.avail:
                analyzer = self.get_scan(scan_id).get_scaninfo(get_analyzer=True)
                if visu := analyzer.visu_pars:
                    setattr(self, 'study_ref', visu)
                    return
    
    def _get_subject(self) -> Optional[Parameter]:
        if not self.contents or 'subject' not in self.contents['files']:
            return None
        return self.subject
    
    def _parse_header(self) -> None:
        """Parses the header information from the study metadata.

        Extracts the header data based on subject and parameters, setting up the
        study header attribute. This method handles cases with different versions
        of ParaVision by adjusting the header format accordingly.
        """
        if subj := self._get_subject():
            subj_header = getattr(subj, 'header') if subj.is_parameter() else {}
            if subj_header:
                if title := subj_header['TITLE']:
                    self.header = OrderedDict(**{k.replace("SUBJECT_", ""): v for k, v in subj.parameters.items() \
                        if k.startswith("SUBJECT")})
                    sw_version = self.parse_version(str(title))
                    if not sw_version:
                        self._fetch_study_ref()
                    self.header['sw_version'] = sw_version
            
    @staticmethod
    def parse_version(version_string: str) -> str:
        """Parse """
        version_regex = r'(?<!\d)\b\d+\.\d+(?:\.\d+)?\b(?!.\d)'
        if version := re.search(version_regex, version_string):
            return version.group(0) 
            
    @property
    def avail(self) -> list:
        """List of available scan IDs within the study.

        Returns:
            list: A list of integers representing the available scan IDs.
        """
        return super().avail

    def info(self, 
             scope: Literal['header', 'scans', 'all'] = 'header', 
             scan_id: Union[int, List[int], None] = None) -> dict:
        if not self.header:
            self._parse_header()
            self._process_header()
            self._streamed_info = self._stream_info()
        if scope == 'all':
            if len(self._streamed_info['scans']) < len(self.avail):
                self._update_stream(self.avail)
            return self._streamed_info
        else:
            info_obj = self._streamed_info[scope]
            if scope == 'scans':
                if not scan_id:
                    scan_id = self.avail
                elif isinstance(scan_id, int):
                    scan_id = [scan_id]
                scans = {}
                if sids := [s for s in scan_id if not s in self._streamed_info['scans'].keys()]:
                    self._update_stream(sids)
                for sid in scan_id:
                    scans[sid] = self._streamed_info['scans'][sid]
                return scans
            else:
                return info_obj
    
    def _update_stream(self, scan_ids):
        self._process_scans(scan_ids)
        self._streamed_info = self._stream_info()
    
    def _stream_info(self):
        stream = copy(self._info.__dict__)
        stream['header']['AvailScanIDs'] = self.avail
        scans = {}
        for scan_id, s in self._info.scans.items():
            scans[scan_id] = s.header
            recos = {}
            for r in s.recos:
                recos[r.reco_id] = r.header
            if recos:
                scans[s.scan_id]['recos'] = recos
        stream['scans'] = scans
        return OrderedDict(**stream)
    
    def _import_spec(self, spec_path: Optional[str] = None):
        if not self._spec:
            spec_path = spec_path or os.path.join(os.path.dirname(__file__), 'study.yaml')
            with open(spec_path, 'r') as f:
                self._spec = yaml.safe_load(f)
    
    def _process_header(self):
        """Compiles comprehensive information about the study, including header details and scans.

        Uses external YAML configuration to drive the synthesis of structured information about the study,
        integrating data from various scans and their respective reconstructions.

        Returns:
            dict: A dictionary containing structured information about the study, its scans, and reconstructions.
        """
        if not self.header:
            self._fetch_study_ref()
        self._info = StudyHeader(header=RecipeParser(self, copy(self._spec)['study']).get(), 
                                 scans={})
    
    def _process_scans(self, scan_ids: List[int]):
        for scan_id in scan_ids:
            self._info.scans[scan_id] = self._process_scan(scan_id)
    
    def _process_scan(self, scan_id: int):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with self.get_scan(scan_id) as scanobj:
                scan_spec = copy(self._spec)['scan']
                scaninfo_targets = scanobj.info
                scan_header = ScanHeader(scan_id=scan_id, 
                                         header=RecipeParser(scaninfo_targets, scan_spec).get(), 
                                         recos=[])
                for reco_id in scanobj.avail:
                    recoinfo_targets = [scanobj.get_scaninfo(reco_id=reco_id)]
                    reco_spec = copy(self._spec)['reco']
                    parsed_reco = RecipeParser(recoinfo_targets, reco_spec).get()
                    reco_header = RecoHeader(reco_id=reco_id, 
                                             header=parsed_reco) if parsed_reco else None
                    if reco_header:
                        scan_header.recos.append(reco_header)
                return scan_header
                
