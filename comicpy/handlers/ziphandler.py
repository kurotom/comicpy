# -*- coding: utf-8 -*-
"""
Handler related to files ZIP.
"""

from comicpy.handlers.imageshandler import ImagesHandler
from comicpy.utils import Paths

from comicpy.models import (
    CurrentFile,
    CompressorFileData
)
from comicpy.handlers.baseziprar import BaseZipRarHandler

from comicpy.valid_extentions import ValidExtentions

import tempfile
import pyzipper
import zipfile
import io

from typing import List, Union, TypeVar

PRESERVE = TypeVar('preserve')
SMALL = TypeVar('small')
MEDIUM = TypeVar('medium')
LARGE = TypeVar('large')


class ZipHandler(BaseZipRarHandler):
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
        self.TEMPDIR = tempfile.gettempdir()
        self.type = 'zip'
        self.imageshandler = ImagesHandler()
        self.validextentions = ValidExtentions()
        self.paths = Paths()
        self.number_index = 0

    def testZip(
        self,
        currentFileZip: CurrentFile
    ) -> bool:
        """
        Checks if ZIP file is password protected.

        Args:
            currentFileZip: `CurrentFile` instance with raw data of file ZIP.

        Returns:
            bool: `True` if password protected, otherwise, retuns `False`.
        """
        try:
            with zipfile.ZipFile(
                currentFileZip.bytes_data,
                mode='r'
            ) as fileZip:
                fileZip.testzip()
            return False
        except RuntimeError:
            return True

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

    def extract_content(
        self,
        currentFileZip: CurrentFile,
        password: str = None,
        is_join: bool = False,
        resizeImage: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[CompressorFileData, None]:
        """
        Extract images from ZIP file.

        Args:
            currentFile: `CurrentFile` instance with data of original ZIP file.
            password: password string of file, default is `None`.
            imageSize: string of size image. Default is `'small'`.

        Returns:
            CompressorFileData: instances contains name of directory of images,
                                list of ImageComicData instances, type of
                                compressor.
        """
        bytesZipFile = currentFileZip.bytes_data

        with pyzipper.AESZipFile(
            bytesZipFile,
            mode='r',
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES
        ) as zip_file:

            if password is not None:
                zip_file.pwd = password.encode('utf-8')

            zipFileOrigin = super().iterateFiles(
                instanceCompress=zip_file,
                password=password,
                resize=resizeImage,
                type_compress='zip',
                join=is_join
            )

            if zipFileOrigin is not None:
                if zipFileOrigin.filename == '':
                    zipFileOrigin.filename = currentFileZip.name

            return zipFileOrigin

    def to_zip(
        self,
        listZipFileCompress: List[CompressorFileData],
        join: bool,
        filenameZIP: str = None
    ) -> Union[List[CurrentFile], None]:
        """
        Handles how the data in the ZIP file(s) should be written.

        Args:
            listZipFileCompress: list of `CompressorFileData` instances.
            filenameZIP: name of the ZIP archive.
            join: if `True` merge all files, otherwise, no.

        Returns:
            List[CurrentFile]: list of `CurrentFile` instances contains bytes
                               of the ZIP files.
            None: if this process fail.
        """
        if len(listZipFileCompress) == 0:
            return None

        # print(listZipFileCompress, type(listZipFileCompress))
        # print(len(listZipFileCompress), join)

        data_of_zips = []
        if join is True:
            currentFileZip = self.__to_zip_data(
                    listZipFileCompress=listZipFileCompress,
                    filenameZIP=filenameZIP
                )
            data_of_zips.append(currentFileZip)
        elif join is False:
            for file in listZipFileCompress:

                current_file_list = [file]
                currentFileZip = self.__to_zip_data(
                            listZipFileCompress=current_file_list,
                            filenameZIP=file.filename
                        )
                data_of_zips.append(currentFileZip)

        return data_of_zips

    def __to_zip_data(
        self,
        listZipFileCompress: List[CompressorFileData],
        filenameZIP: str = None,
    ) -> CurrentFile:
        """
        Write data of `CompressorFileData` into ZIP file.

        Args:
            listZipFileCompress: list of `CompressorFileData` instances with
                                 ZIP compressor data.
            filenameZIP: name of file ZIP.

        Returns:
            CurrentFile: with data of ZIP file.
        """

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

                info_file_zip = zipfile.ZipInfo(filename=directory_path)
                info_file_zip.compress_type = zipfile.ZIP_DEFLATED

                for image in item.list_data:
                    image_path = self.paths.build(
                                            directory_path,
                                            image.filename
                                        )
                    zip_file.writestr(
                            zinfo_or_arcname=image_path,
                            data=image.bytes_data.getvalue()
                        )

        zipFileCurrent = CurrentFile(
                            filename=filenameZIP,
                            bytes_data=buffer_dataZip,
                            unit=self.unit,
                            extention='.cbz'
                        )
        return zipFileCurrent

    def to_write(
        self,
        currentFileZip: CurrentFile
    ) -> List[dict]:
        """
        Send data to `BaseZipRarHandler.to_write()` to save the ZIP file data.

        Args:
            currentFileRar: `CompressorFileData` instance, contains data of
                            ZIP file.

        Returns:
            List[dict]: list of dicts with information of all files saved.
                        'name': path to the file.
                        'size': size of file.
        """
        return super().to_write(currentFileInstance=currentFileZip)
