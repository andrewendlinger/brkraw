from xnippet import XnippetManager
from xnippet import setup_logging

__version__ = '0.4.0a1'

config = XnippetManager(package_name=__package__, 
                        package_version=__version__,
                        package__file__=__file__,
                        config_filename='config.yaml')

def parse_app_config(name_):
    name = name_.split('.')[-1]
    if name in config.config['app']:
        return config.config['app'][name]
    return None

__all__ = ['__version__', 'config', 'setup_logging', 'parse_app_config']
