import click
from brkraw import __version__
from .tonifti import tonii
from .viewer import viewer as viewer_
from .bids import bids as bids_
from .manager import manager as manager_


@click.group()
@click.version_option(version=__version__, prog_name='brkraw')
def main():
    """BrkRaw command-line interface"""
    pass
        
@main.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('-s', '--scan-id', type=int, multiple=True, default=(), help='Accept multiple scan IDs.')
def info(input):
    """Prints out the information of the internal contents in Bruker Paravision Dataset."""
    from brkraw.api import StudyData
    study = StudyData(input)
    study.info('all')
    
main.add_command(tonii)
main.add_command(viewer_)
main.add_command(bids_)
main.add_command(manager_)
    
if __name__ == '__main__':
    main()