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

# from uuid import uuid1
# import tempfile
# import io

import warnings

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
        self.type = 'zip'
        self.imageshandler = ImagesHandler()
        self.validextentions = ValidExtentions()
        self.paths = Paths()
        self.number_index = 1

        self.FILE_CBZ_ = None
        self.FILE_ZIP_ = None
        self.CONVERTED_COMICPY_PATH_ = None

        warnings.filterwarnings("ignore", category=UserWarning)

    def reset_names(self) -> None:
        """
        Resets attributes of instance.
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
    ) -> Union[CompressorFileData, None, int]:
        """
        Extract images from ZIP file.

        Args:
            currentFileZip: `CurrentFile` instance with data of original ZIP
                            file.
            password: password string of file, default is `None`.
            is_join: `True` to join into one, otherwise no.
            resizeImage: string of size image. Default is `'small'`.

        Returns:
            CompressorFileData: instances contains name of directory of images,
                                list of ImageComicData instances, type of
                                compressor.
            int: `-1` if password is incorrect.
            None: if has an error ocurrs.
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
        pathCBZconverted: str,
        basedir: str,
        data_list: List[CompressorFileData] = None,
        last_item: bool = False
    ) -> List[dict]:
        """
        It groups the raw data into a ZIP file and renames it with a CBZ
        extension.

        Args
            join: boolean, `True` to join, otherwise, `False`.
            converted_comicpy_path: directory path to all CBZ files.
            pathCBZconverted: path of CBZ file.
            basedir: name of directory base of CBZ file.
            data_list: list of raw data content of ZIP file.
            last_item: boolean indicates last item of list of content of ZIP
                       file.

        Returns
            list: list of diccionaries with metadata of file/s CBZ.
        """
        if data_list is None:
            return None

        # Reset names CBZ, ZIP.
        if join is False:
            self.reset_names()

        metadata_zip = []
        first_directory = False
        ITEM_DIR_ = None

        name_, extention = self.paths.splitext(
                                self.paths.get_basename(pathCBZconverted)
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

            # print(pathCBZconverted, ITEM_DIR_, self.CONVERTED_COMICPY_PATH_)

            self.FILE_CBZ_ = pathCBZconverted

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

        if join:
            if last_item:
                meta = super().get_metadata(path=self.FILE_CBZ_)
                metadata_zip.append(meta)

        else:
            meta = super().get_metadata(path=self.FILE_CBZ_)
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
