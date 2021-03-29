"""
Utils
"""

import click


def exception_handler(func):
    """
    Base exception handler.
    Handle ValueError and
    write it to the command line using click
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            click.echo(str(exc))
        return None

    return wrapper
