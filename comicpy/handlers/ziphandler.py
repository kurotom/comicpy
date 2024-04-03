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

from comicpy.exceptionsClasses import BadPassword

import pyzipper
import zipfile

from uuid import uuid1


import tempfile
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
        # self.TEMPDIR = tempfile.gettempdir()
        self.type = 'zip'
        self.imageshandler = ImagesHandler()
        self.validextentions = ValidExtentions()
        self.paths = Paths()
        self.number_index = 1

        self.FILE_CBZ_ = None
        self.FILE_ZIP_ = None
        self.CONVERTED_COMICPY_PATH_ = None

    def reset_names(self) -> None:
        """
        """
        self.FILE_CBZ_ = None
        self.FILE_ZIP_ = None
        self.CONVERTED_COMICPY_PATH_ = None

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

        try:
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
        except BadPassword as e:
            print(e)
            return -1
        except Exception:
            return None

    def to_zip(
        self,
        join: bool,
        converted_comicpy_path: str,
        filenameZIP: str,
        basedir: str,
        data_list: List[CompressorFileData] = None,
    ) -> List[dict]:
        """
        """
        if data_list is None:
            return None

        # Reset names CBZ, ZIP.
        if join is False:
            self.reset_names()

        to_zip_directories = []
        metadata_zip = []
        first_directory = False
        ITEM_DIR_ = None

        name_, extention = self.paths.splitext(
                                self.paths.get_basename(filenameZIP)
                            )

        self.CONVERTED_COMICPY_PATH_ = self.paths.build(
                                    converted_comicpy_path.replace(' ', '_'),
                                    make=True
                                )

        # DELETE THIS
        # join = True  # DELETE THIS
        # DELETE THIS
        # print(self.FILE_CBZ_, self.FILE_ZIP_)

        for item in data_list:
            # names_dir = self.paths.get_dirname(item.filename)
            # name_item = self.paths.get_basename(item.filename)
            # print('-> ', name_item)
            if join is True:
                if first_directory is False:
                    ITEM_DIR_ = self.paths.get_dirname_level(
                                                item.filename,
                                                level=-1
                                            )
                first_directory = True
            else:
                ITEM_DIR_ = self.paths.get_dirname_level(
                                            item.filename,
                                            level=-1
                                        )

            if ITEM_DIR_ == '.':
                ITEM_DIR_ = name_

            ITEM_DIR_ = ITEM_DIR_.replace(' ', '_')

            # print(join, filenameZIP, ITEM_DIR_, self.CONVERTED_COMICPY_PATH_)

            cbz_file_name = self.paths.build(
                                self.CONVERTED_COMICPY_PATH_,
                                '%s.cbz' % (ITEM_DIR_)
                            )

            if join:
                if self.FILE_CBZ_ is None:
                    self.FILE_CBZ_ = cbz_file_name
            else:
                self.FILE_CBZ_ = cbz_file_name

            with zipfile.ZipFile(
                file=self.FILE_CBZ_, mode='a',
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=False
            ) as zip_file:

                directory_path = item.filename

                info_file_zip = zipfile.ZipInfo(filename=directory_path)
                info_file_zip.compress_type = zipfile.ZIP_DEFLATED

                zip_file.writestr(
                        zinfo_or_arcname=item.filename,
                        data=item.bytes_data.getvalue()
                    )
            if cbz_file_name not in to_zip_directories:
                to_zip_directories.append(cbz_file_name)

        for cbz_path in to_zip_directories:
            # print(cbz_path)
            size = self.paths.get_size(path=cbz_path, unit=self.unit)
            meta = {
                'name': cbz_path,
                'size': '%.2f %s' % (
                            size,
                            self.unit.upper()
                    )
            }
            metadata_zip.append(meta)
        return metadata_zip

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
