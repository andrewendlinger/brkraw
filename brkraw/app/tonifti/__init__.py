"""
dependency:
    bids, plugin
"""
from brkraw import __version__, parse_app_config
from brkraw.app.tonifti.plugin import ToNiftiPlugin, PvScan, PvReco, PvFiles
from brkraw.app.tonifti.study import StudyToNifti, ScanToNifti

app_config = parse_app_config(__name__)

__all__ = ['ToNiftiPlugin', 'StudyToNifti', 'ScanToNifti', 'PvScan', 'PvReco', 'PvFiles']
