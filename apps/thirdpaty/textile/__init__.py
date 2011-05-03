from apps.thirdpaty.textile.functions import textile, textile_restricted, Textile

__all__ = ['textile', 'textile_restricted']

def render_textile(value):
    return textile(value)
