# -*- coding: utf-8 -*-
"""
Utils
"""

import os

from typing import Union, Tuple


class Paths:
    DIR = 'comicpyData'
    HOME_DIR = os.path.expanduser('~')
    ROOT_PATH = os.path.join(HOME_DIR, DIR)

    def build(
        self,
        *path: Union[str, Tuple[str]]
    ) -> str:
        path_ = os.path.join(*path)
        self.check_and_create(path=path_)
        return path_

    def check_and_create(
        self,
        path: str
    ) -> None:
        if not os.path.exists(path):
            os.makedirs(path)
