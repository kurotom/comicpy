# -*- coding: utf-8 -*-
"""
"""

from comicpy.models import (
    ImageComicData,
    CurrentFile
)

import zipfile
import io

from typing import TypeVar, List


ImageComicDataInstance = TypeVar('ImageComicDataInstance')
CurrentFileInstance = TypeVar('CurrentFileInstance')


class ZipHandler:

    def rename_zip_cbz(
        self,
        currentFileZip: CurrentFileInstance
    ) -> None:
        currentFileZip.extention = '.cbz'
        currentFileZip.name = currentFileZip.name.replace(' ', '_')
        return currentFileZip

    def to_zip(
        self,
        listImageComicData: List[ImageComicDataInstance]
    ) -> CurrentFile:
        buffer_data = io.BytesIO()
        with zipfile.ZipFile(
            file=buffer_data, mode='a',
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=False
        ) as zip_file:
            for item in listImageComicData:
                zip_file.writestr(
                        zinfo_or_arcname=item.filename,
                        data=item.bytes_data.getvalue()
                    )

        zipFileCurrent = CurrentFile(
                            filename='FileZip',
                            bytes_data=buffer_data,
                        )
        return zipFileCurrent

    def to_write(
        self,
        currentFileZip: CurrentFileInstance
    ) -> dict:
        fileZip = currentFileZip.name + currentFileZip.extention
        with open(fileZip, 'wb') as file:
            file.write(currentFileZip.bytes_data.getvalue())

        return {
            'zip_name': fileZip,
            'size': currentFileZip.size
        }
