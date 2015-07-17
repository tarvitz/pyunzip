from apps.thirdpaty.textile.functions import (
    textile, textile_restricted, Textile)
from apps.thirdpaty.textile.textilefactory import TextileFactory


def render_textile(value):
    t = TextileFactory()
    return t.process(value)

__all__ = ['textile', 'textile_restricted', 'render_textile', 'Textile']
