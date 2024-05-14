import click
from brkraw import __version__, parse_app_config

app_config = parse_app_config(__name__)

@click.group()
def bids():
    """Sub-command for BIDS organization helper."""
    pass

@bids.command()
def helper():
    print(__name__)

if __name__ == "__main__":
    bids()