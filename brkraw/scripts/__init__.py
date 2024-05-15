import click
from brkraw import __version__
from .tonifti import tonii
from .viewer import viewer as viewer_
from .bids import bids as bids_
from .manager import manager as manager_
from .utils import process_study_info, prep_scan_info

@click.group()
@click.version_option(version=__version__, prog_name='brkraw')
def main():
    """BrkRaw command-line interface"""
    pass
        
@main.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('-s', '--scan_id', type=int, multiple=True, default=(), help='Print onlt Selcted scans. Accept multiple ScanIDs.')
@click.option('-a', '--all', is_flag=True, default=False, help='Print out all available scans.')
def info(input, scan_id, all):
    """Prints out the information of the internal contents in Bruker Paravision Dataset."""
    from brkraw.api import StudyData
    study = StudyData(input)
    study_lines, max_chars = process_study_info(study, all)
    print("\n".join(study_lines) + "\n")
    if all or scan_id:
        scan_id = study.avail if all else scan_id
        scan_lines = prep_scan_info(study, scan_id, max_chars)
        print("\n".join(scan_lines) + "\n")

main.add_command(tonii)
main.add_command(viewer_)
main.add_command(bids_)
main.add_command(manager_)

if __name__ == '__main__':
    main()