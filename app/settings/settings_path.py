# coding: utf-8

import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir)
)

sys.path.insert(0, PROJECT_ROOT)


def rel_path(subdir):
    return os.path.join(
        os.path.join(PROJECT_ROOT, os.path.pardir), subdir
    )
