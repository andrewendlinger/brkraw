from xnippet import XnippetManager
from xnippet import setup_logging

__version__ = '0.4.0a1'

config = XnippetManager(package_name=__package__, 
                        package_version=__version__,
                        package__file__=__file__,
                        config_filename='config.yaml')

def main():
    print(f'Hello, Brkraw {__version__}')

if __name__ == '__main__':
    main()

__all__ = ['__version__', 'config', 'setup_logging']