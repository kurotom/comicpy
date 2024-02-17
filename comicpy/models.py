# -*- coding: utf-8 -*-
"""
"""

import io
import os


SizeUnits = {
    'b': 10**1,
    'kb': 10**3,
    'mb': 10**6,
    'gb': 10**9
}


class FileBaseClass:

    def get_extention(
        self,
    ) -> None:
        data = os.path.splitext(self.filename)
        self.name = data[0]
        self.extention = data[1].lower()

    def get_size(
        self,
    ) -> int:
        try:
            size_unit = SizeUnits[self.unit]
        except KeyError:
            self.unit = 'mb'
            size_unit = SizeUnits[self.unit]
        size_buffer = self.bytes_data.getbuffer().nbytes / size_unit
        return size_buffer

    def __str__(self) -> str:
        return '<[Name: "%s", Size: "%.2f %s"]>' % (
                        self.filename,
                        self.size,
                        self.unit.upper()
                )


class ImageComicData(FileBaseClass):

    def __init__(
        self,
        filename: str,
        bytes_data: io.BytesIO,
        extention: str = None,
        unit: str = 'mb'
    ) -> None:
        self.filename = filename
        self.extention = extention
        self.bytes_data = bytes_data
        self.name = None
        self.unit = unit
        self.size = super().get_size()
        super().get_extention()

    def __str__(self) -> str:
        return super().__str__()


class CurrentFile(FileBaseClass):

    def __init__(
        self,
        filename: str,
        bytes_data: io.BytesIO,
        chunk_bytes: bytes = None,
        extention: str = None,
        unit: str = 'mb'
    ) -> None:
        self.filename = filename
        self.extention = extention
        self.chunk_bytes = chunk_bytes
        self.bytes_data = bytes_data
        self.name = None
        self.unit = unit
        self.size = super().get_size()
        super().get_extention()

    def __str__(self) -> str:
        return super().__str__()
