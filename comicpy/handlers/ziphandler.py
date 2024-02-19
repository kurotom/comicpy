# -*- coding: utf-8 -*-
"""
"""

from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData
)
from comicpy.valid_extentions import imagesExtentions

import zipfile
import io
import os

from typing import List


class ZipHandler:

    def rename_zip_cbz(
        self,
        currentFileZip: CurrentFile
    ) -> CurrentFile:
        currentFileZip.extention = '.cbz'
        currentFileZip.name = currentFileZip.name.replace(' ', '_')
        return currentFileZip

    def extract_images(
        self,
        currentFileZip: CurrentFile
    ) -> CompressorFileData:

        listImageComicData = []
        directory_name = None
        dataBytesIO = currentFileZip.bytes_data

        with zipfile.ZipFile(
            file=dataBytesIO, mode='r'
        ) as zip_file:

            for item in zip_file.namelist():

                directory_name = os.path.dirname(item).replace(' ', '_')
                name_file = os.path.basename(item)
                _name, _extention = os.path.splitext(name_file)

                if _extention in list(imagesExtentions.values()):
                    # print(_name, _extention, directory_name)
                    item_name = name_file.replace(' ', '_')
                    file_name = '%s_%s' % (directory_name, item_name)

                    dataImage = zip_file.read(item)
                    image_comic = ImageComicData(
                                    filename=file_name,
                                    bytes_data=io.BytesIO(dataImage)
                                )
                    listImageComicData.append(image_comic)

        zipFileCompress = CompressorFileData(
                                    filename=directory_name,
                                    list_data=listImageComicData,
                                    type='zip',
                                )
        return zipFileCompress


    def to_zip(
        self,
        listZipFileCompress: List[CompressorFileData]
    ) -> CurrentFile:
        buffer_dataZip = io.BytesIO()
        with zipfile.ZipFile(
            file=buffer_dataZip, mode='a',
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=False
        ) as zip_file:
            for item in listZipFileCompress:
                # print(item, len(item.list_data), item.filename)

                directory_path = item.filename

                info_archivo_zip = zipfile.ZipInfo(filename=directory_path)
                info_archivo_zip.compress_type = zipfile.ZIP_DEFLATED

                for image in item.list_data:
                    image_path = '%s/%s' % (directory_path, image.filename)
                    zip_file.writestr(
                            zinfo_or_arcname=image_path,
                            data=image.bytes_data.getvalue()
                        )

        zipFileCurrent = CurrentFile(
                            filename='FileZip',
                            bytes_data=buffer_dataZip,
                        )
        return zipFileCurrent

    def to_write(
        self,
        currentFileZip: CurrentFile
    ) -> dict:
        fileZip = currentFileZip.name + currentFileZip.extention
        with open(fileZip, 'wb') as file:
            file.write(currentFileZip.bytes_data.getvalue())

        return {
            'name': fileZip,
            'size': '%.2f %s' % (
                            currentFileZip.size,
                            currentFileZip.unit.upper()
                        )
        }
