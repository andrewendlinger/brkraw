from __future__ import annotations
from typing import TYPE_CHECKING
from .base import BaseHelper
if TYPE_CHECKING:
    from ..analyzer import ScanInfoAnalyzer

class SeqParams(BaseHelper):
    """_summary_
    Helper class to parse protocol parameters for data acqusition form 'acqp' file

    Args:
        BaseHelper (_type_): _description_
    """
    def __init__(self, analobj: 'ScanInfoAnalyzer'):
        super().__init__()
        
        acqp = analobj.acqp
        if not acqp:
            self._warn(f"Failed to fetch all Sequence Parameter information because the 'acqp' file is missing from 'analobj'.")
        
        self.echo_time = acqp.get("ACQ_echo_time")
        self.repetition_time = acqp.get("ACQ_repetition_time")
        self.effbw = acqp.get("SW_h")
        self.flip_angle = acqp.get("ACQ_flip_angle")
        self.n_echo_images = acqp.get("ACQ_n_echo_images")
            
    def get_info(self):
        return {
            "echo_time": self.echo_time,
            "repetition_time": self.repetition_time,
            "effbw": self.effbw,
            "flip_angle": self.flip_angle,
            "n_echo_images": self.n_echo_images,
        }