# coding: utf-8
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.path.pardir))


def rel_path(subdir):
    return os.path.join(PROJECT_ROOT, subdir)

if __name__ in '__main__':
    pass
