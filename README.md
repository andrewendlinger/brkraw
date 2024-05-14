[![DOI](https://zenodo.org/badge/245546149.svg)](https://zenodo.org/badge/latestdoi/245546149)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/BrkRaw/tutorials/main)

## BrkRaw: A Comprehensive and Extensible Converter for Bruker Paravision Datasets
#### Version: 0.4.0a1
### Description

BrkRaw is a Python module designed to efficiently handle raw Bruker Paravision datasets from Biospin preclinical MRI scanners. 
It simplifies the conversion of images to the Nifti1 format, which is widely recognized by analysis software, 
and ensures compliance with the [BIDS standard](https://bids-specification.readthedocs.io/en/stable/). 
BrkRaw features a robust metadata parser and supports custom extensions, 
allowing users to add new functionalities seamlessly without modifying the existing codebase.

The module encompasses four primary applications:
- **tonifti**: The key module for conversion, currently the only active app in this alpha testing phase.
- **backup**: Designed for data archiving, to be integrated atop tonifti to maintain integrity.
- **bids**: A semi-automated converter that transforms multiple raw datasets into a complete BIDS-compliant structure with the aid of simple datasheets and recipes.
- **viewer**: A straightforward graphical user interface that allows for the viewing of raw data and metadata without conversion.

> **Please Note**: In the current pre-release version undergoing alpha testing, only the tonifti application is activated for testing purposes. 
Future updates will enable the backup, bids, and viewer features, all integrated within the tonifti framework to ensure cohesive functionality across the built-in applications.
If you are looking for a fully functional version, please refer to the [`release 0.3.11`](https://github.com/BrkRaw/brkraw/tree/0.3.11-post1).


### Website

For detailed information including installation, usage examples, and more, please visit our [GitPage](https://brkraw.github.io):

- [Installation](https://brkraw.github.io/docs/gs_inst.html)
- [Command-line tool usage examples](https://brkraw.github.io/docs/gs_nii.html)
- [Converting dataset into BIDS](https://brkraw.github.io/docs/gs_bids.html)
- [Python API usage examples](https://brkraw.github.io/docs/ap_parent.html)
- [GUI](https://brkraw.github.io/docs/gs_gui.html)
- [Interactive Tutorial](https://mybinder.org/v2/gh/BrkRaw/tutorials/ac95b2c87b05664cb678c5dc1a930641397130ed)

> **Please Note**: The current documents are outdated and are in the process of being updated. We appreciate your patience and encourage you to check back soon for the most recent information.

### Acknowledgements
We are grateful to all the contributors who have played a significant role in the development and advancement of this project. For a detailed list of acknowledgements, please refer to our [Acknowledgements page](ACKNOWLEDGEMENTS.md).


### License
This project is licensed under the GNU General Public License v3.0. For more details, please see the [GPLv3 License](LICENSE).

### Contributing

We welcome contributions from the community. For guidelines on how to get involved, please refer to our [Contributing Guidelines](CONTRIBUTING.md).

### Citation

If you use BrkRaw in your research, please cite it according to the information provided in our [CITATION.cff file](CITATION.cff).
