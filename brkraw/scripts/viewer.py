import click

@click.group()
def viewer():
    """Sub-command for Graphical User Interface."""
    pass

if __name__ == '__main__':
    viewer()