import click
from brkraw.app.tonifti import StudyToNifti, ScanToNifti
from brkraw.types import KeyValuePairs

def print_help_msg(ctx, param, value):
    if not value or not any(value):
        click.echo(ctx.get_help())
        ctx.exit()


@click.group()
@click.argument('inputs', nargs=-1, type=click.Path(exists=True), callback=print_help_msg)
@click.option('-m', '--scale-mode', default='', type=click.Choice(['header', 'apply', 'none'], case_sensitive=False))
@click.pass_context
def tonii(ctx, inputs, scale_mode):
    """Sub-command for converting to NifTi1 format."""
    scale_mode = None if scale_mode == 'none' else scale_mode
    studyobj = 'StudyToNifti Placeholder'  # Placeholder for the actual StudyToNifti initialization
    ctx.obj = {
        "studyobj": studyobj,
        "scale_mode": scale_mode
    }

@tonii.command()
@click.argument('scan_ids', nargs=-1, type=int)
@click.argument('reco_ids', nargs=-1, type=int)
@click.option('-p', '--plugin', help="Specify the plugin to use.")
@click.option('--config', cls=KeyValuePairs, help="Extra configuration in key=value format, multiple can be joined by ','.")
@click.pass_context
def scans(ctx, scan_ids, reco_ids, plugin, config):
    """Convert whole study or selected scans; if reco_id given, convert those specifically."""
    click.echo(f"Study Object: {ctx.obj['studyobj']}")
    click.echo(f"Scale Mode: {ctx.obj['scale_mode']}")
    click.echo(f"Scan IDs: {scan_ids}, Reco IDs: {reco_ids}")
    click.echo(f"Using plugin: {plugin}")
    click.echo(f"Configuration: {config}")

@tonii.command()
@click.pass_context
def all(ctx):
    """Convert all available data."""
    click.echo(f"Converting all data with settings: {ctx.obj}")

if __name__ == '__main__':
    tonii()