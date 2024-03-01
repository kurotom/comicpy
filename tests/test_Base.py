# -*- coding: utf-8 -*-
"""
Tests Base
"""


from comicpy.comicpy import ComicPy
from comicpy.utils import Paths

from comicpy.models import (
    CurrentFile,
    CompressorFileData
)

import unittest
import os
import sys
import io


class BaseTestCase(unittest.TestCase):

    TESTS_DIR = 'tests'
    TEMP_DIR = 'TEMP_DIR'
    BIN_RAR = 'bin'

    FILES = {
        'empty.pdf': 'tests/files/empty.pdf',
        'empty.rar': 'tests/files/empty.rar',
        'empty.zip': 'tests/files/empty.zip',

        'no_image.zip': 'tests/files/no_image.zip',
        'no_image.rar': 'tests/files/no_image.rar',

        'protected_image_dir_2.zip': 'tests/files/image_dir_2_protected.zip',
        'protected_image_dir_2.rar': 'tests/files/image_dir_2_protected.rar',

        'cbr_comic.zip': 'tests/files/cbr_comic.zip',
        'cbr_comic.rar': 'tests/files/cbr_comic.rar',

        'file.pdf': 'tests/files/file.pdf',
        'image.pdf': 'tests/files/image.pdf',

        'image_dir_1.zip': 'tests/files/image_dir_1.zip',
        'image_dir_1.rar': 'tests/files/image_dir_1.rar',
        'image_dir_2.zip': 'tests/files/image_dir_2.zip',
        'image_dir_2.rar': 'tests/files/image_dir_2.rar',

        'image_dir_2.cbr': 'tests/files/image_dir_2.cbr',
        'image_dir_2.cbz': 'tests/files/image_dir_2.cbz'
    }

    DIRS = {
        'pdfs': 'tests/files/pdfs',
        'zips': 'tests/files/zips',
        'rars': 'tests/files/rars',
        'rars_protected': 'tests/files/rars_protected',
        'zips_protected': 'tests/files/zips_protected',
        'images_dir': 'tests/files/images_dir',
        'cbr_cbz': 'tests/files/cbr_cbz',
        'no_image_zip_rar': 'tests/files/no_image_zip_rar'
    }

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.pdfs_dir = BaseTestCase.DIRS['pdfs']
        self.zips_dir = BaseTestCase.DIRS['zips']
        self.rars_dir = BaseTestCase.DIRS['rars']
        self.images_dir = BaseTestCase.DIRS['images_dir']
        self.cbr_cbz_dir = BaseTestCase.DIRS['cbr_cbz']
        self.rars_protected = BaseTestCase.DIRS['rars_protected']
        self.zips_protected = BaseTestCase.DIRS['zips_protected']
        self.no_image_zip_rar = BaseTestCase.DIRS['no_image_zip_rar']

        self.paths = Paths()
        self.temp_dir = self.make_temp_dir()

        self.comicpy = ComicPy
        self.comicpy_init = ComicPy()
        self.files = BaseTestCase.FILES
        self.dirs = BaseTestCase.DIRS
        self.data = {}
        self.loadContent()

    def make_temp_dir(self):
        path = self.paths.build(
                    BaseTestCase.TESTS_DIR, BaseTestCase.TEMP_DIR,
                    make=True)
        return path

    def loadContent(self) -> dict:
        keys = list(BaseTestCase.FILES.keys())
        raw_data = []
        for name, path in BaseTestCase.FILES.items():
            raw_data.append(self.read(file=path))
        self.data = dict(zip(keys, raw_data))

    def read(
        self,
        file: str
    ) -> bytes:
        with open(file, 'rb') as fl:
            return fl.read()

    def buid_CurrentFile(
        self,
        filename: str,
        raw_data: bytes,
        extention: str = None,
        return_valid: bool = True
    ) -> CurrentFile:
        currentFile = CurrentFile(
                        filename=filename,
                        bytes_data=io.BytesIO(raw_data),
                        chunk_bytes=raw_data[:8],
                        unit='mb'
                    )
        if extention is not None:
            currentFile.extention = extention
        if return_valid is False:
            currentFile.chunk_bytes = raw_data[8:16]

        return currentFile
