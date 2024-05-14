import click

class KeyValuePairs(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            if value:
                # Split each provided option on '=', and create a dictionary from them
                return dict(item.split('=') for item in value.split(','))
            return {}
        except ValueError:
            raise click.BadParameter("Key-value pairs must be in key=value format separated by commas without spaces.")
        
__all__ = ['KeyValuePairs']