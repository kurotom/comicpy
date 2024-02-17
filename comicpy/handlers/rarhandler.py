# -*- coding: utf-8 -*-
"""
"""


from comicpy.models import (
    ImageComicData,
    CurrentFile
)

import io

from typing import TypeVar


ImageComicDataInstance = TypeVar('ImageComicDataInstance')
CurrentFileInstance = TypeVar('CurrentFileInstance')


class RarHandler:

    def rename_rar_cbr(
        self,
        currentFileRar: CurrentFileInstance
    ) -> None:
        currentFileRar.extention = '.cbr'
        currentFileRar.name = currentFileRar.name.replace(' ', '_')
        return currentFileRar

    def to_rar(
        self,
        listImageComicData: ImageComicData
    ) -> io.BytesIO:
        pass

    def to_write(
        self,
        currentFileZip: CurrentFileInstance
    ) -> dict:
        fileZip = currentFileZip.name + currentFileZip.extention
        with open(fileZip, 'wb') as file:
            file.write(currentFileZip.bytes_data.getvalue())

        return {
            'rar_name': fileZip,
            'size': currentFileZip.size
        }
