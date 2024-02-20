# -*- coding: utf-8 -*-
"""
Handler related to files ZIP.
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

from typing import List, Union


class ZipHandler:
    """
    Class in charge of extract images, rename file ZIP, create ZIP file, write
    data into ZIP file.
    """

    def __init__(
        self,
        unit: str
    ) -> None:
        """
        Constructor.

        Args:
            unit: indicate unit of measure using to represent file size.
        """
        self.unit = unit

    def rename_zip_cbz(
        self,
        currentFileZip: CurrentFile
    ) -> CurrentFile:
        """
        Add CBZ name and extention of `CurrentFile` instance.

        Args:
            CurrentFile: instance with data ZIP file.

        Returns:
            CurrentFile: same instance with new name and extention.
        """
        currentFileZip.extention = '.cbz'
        currentFileZip.name = currentFileZip.name.replace(' ', '_')
        return currentFileZip

    def extract_images(
        self,
        currentFileZip: CurrentFile
    ) -> CompressorFileData:
        """
        Extract images from ZIP file.

        Args:
            currentFile:

        Returns:
            CompressorFileData: instances contains name of directory of images,
                                list of ImageComicData instances, type of
                                compressor.
        """
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
                    file_name = os.path.join(directory_name, item_name)

                    dataImage = zip_file.read(item)
                    image_comic = ImageComicData(
                                    filename=file_name,
                                    bytes_data=io.BytesIO(dataImage),
                                    unit=self.unit
                                )
                    listImageComicData.append(image_comic)

        zipFileCompress = CompressorFileData(
                                    filename=directory_name,
                                    list_data=listImageComicData,
                                    type='zip',
                                    unit=self.unit
                                )
        return zipFileCompress

    def to_zip(
        self,
        listZipFileCompress: List[CompressorFileData],
        filenameZIP: str = None,
    ) -> Union[CurrentFile, None]:
        """
        Converts a list of CompressorFileData instances to a ZIP archive.

        Args:
            listZipFileCompress: list of CompressorFileData instances.
            filenameZIP: name of the ZIP archive.

        Returns:
            CurrentFile: the instance contains bytes of the ZIP file.
            None: if `subprocess.run` fails.
        """
        if len(listZipFileCompress) == 0:
            return None

        if filenameZIP is None:
            filenameZIP = 'FileZip'

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
                    image_path = os.path.join(directory_path, image.filename)
                    zip_file.writestr(
                            zinfo_or_arcname=image_path,
                            data=image.bytes_data.getvalue()
                        )

        zipFileCurrent = CurrentFile(
                            filename=filenameZIP,
                            bytes_data=buffer_dataZip,
                            unit=self.unit
                        )
        return zipFileCurrent

    def to_write(
        self,
        currentFileZip: CurrentFile
    ) -> dict:
        """
        Writes data to a CBZ file.

        Args:
            CurrentFile: instance with the data in the ZIP file.

        Returns:
            dict: ZIP file information. Keys `'name'`, `'size'`.
        """
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
