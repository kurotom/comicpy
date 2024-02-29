# -*- coding: utf-8 -*-
"""
Base class for ZIP and RAR handlers.
"""

from comicpy.handlers.imageshandler import ImagesHandler
from comicpy.valid_extentions import ValidExtentions
from comicpy.utils import Paths

from comicpy.models import (
    CurrentFile,
    CompressorFileData
)

from rarfile import RarFile
from pyzipper import AESZipFile
import io
from uuid import uuid4

from typing import (
    Union,
    TypeVar
)

ZIP = TypeVar('zip')
RAR = TypeVar('rar')
PRESERVE = TypeVar('preserve')
SMALL = TypeVar('small')
MEDIUM = TypeVar('medium')
LARGE = TypeVar('large')


class BaseZipRarHandler:
    """
    Base class for handler ZIP and RAR.
    """

    def __init__(self) -> None:
        self.paths = Paths()
        self.imageshandler = ImagesHandler()

    def read_file(
        self,
        instanceCompress: Union[RarFile, AESZipFile],
        itemFile: bytes,
        password: str = None,
    ) -> bytes:
        """
        Read data of file, using password for protected files.

        Args
            instanceCompress: `RarFile` or `AESZipFile` instance.
            item: file to read.
            password: password string to unlock the archive data.

        Returns
            bytes: data of file.
        """
        if isinstance(instanceCompress, AESZipFile):
            return instanceCompress.read(itemFile)
        elif isinstance(instanceCompress, RarFile):
            return instanceCompress.read(
                                    itemFile,
                                    pwd=password
                                )

    def exists_valid_files(
        self,
        instanceCompress: Union[RarFile, AESZipFile],
    ) -> bool:
        """
        Checks that the RAR or ZIP file has valid files.

        Args
            instanceCompress: `RarFile` or `AESZipFile` instance.

        Returns
            bool: `True` if exists files valid in the compressor file,
                  otherwise, `False`.
        """
        filters_ = self.validextentions.get_images_extentions()
        filters_ += self.validextentions.get_comic_extentions()
        filters_ = tuple(filters_)
        results = [
                item
                for item in instanceCompress.namelist()
                if item.endswith(filters_)
            ]
        if len(results) > 0:
            return True
        else:
            return False

    def iterateFiles(
        self,
        instanceCompress: Union[RarFile, AESZipFile],
        password: str = None,
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[CompressorFileData, None]:
        """
        Iterates over files of RAR or ZIP files, read their data.

        Args
            instanceCompress: `RarFile` or `AESZipFile` instance.
            password: password string to unlock the archive data.

        Returns:
            CompressorFileData: instances contains name of directory of images,
                                list of ImageComicData instances, type of
                                compressor.
        """
        images_Extentions = self.validextentions.get_images_extentions()
        listContentData = []
        directory_name = None

        files_exists = self.exists_valid_files(
                                instanceCompress=instanceCompress
                            )
        if files_exists is False:
            return None

        for item in instanceCompress.namelist():
            directory_name = self.paths.get_dirname(item).replace(' ', '_')
            name_file = self.paths.get_basename(item)
            _name, _extention = self.paths.splitext(name_file)

            # print(_extention, images_Extentions)

            # print('--> ', _extention.lower(), images_Extentions)

            if _extention.lower() == ValidExtentions.CBR:

                rawDataFile = self.read_file(
                                    instanceCompress=instanceCompress,
                                    itemFile=item,
                                    password=password
                                )

                currentFileCBR = CurrentFile(
                                filename=name_file.replace(' ', '_'),
                                bytes_data=io.BytesIO(rawDataFile),
                                is_comic=True,
                                unit=self.unit
                            )
                listContentData.append(currentFileCBR)

            elif _extention.lower() == ValidExtentions.CBZ:

                rawDataFile = self.read_file(
                                    instanceCompress=instanceCompress,
                                    itemFile=item,
                                    password=password
                                )

                currentFileCBZ = CurrentFile(
                                filename=name_file.replace(' ', '_'),
                                bytes_data=io.BytesIO(rawDataFile),
                                is_comic=True,
                                chunk_bytes=None,
                                unit=self.unit
                            )
                listContentData.append(currentFileCBZ)

            elif _extention.lower() in images_Extentions:

                item_name = '%s%s%s' % (
                    uuid4().hex[:4],
                    _name.replace(' ', '_'),
                    _extention
                )

                file_name = self.paths.build(directory_name, item_name)

                rawDataFile = self.read_file(
                                    instanceCompress=instanceCompress,
                                    itemFile=item,
                                    password=password
                                )

                image_comic = self.imageshandler.new_image(
                                        name_image=file_name,
                                        currentImage=rawDataFile,
                                        extention=_extention[1:].upper(),
                                        sizeImage=resize,
                                        unit=self.unit
                                    )

                listContentData.append(image_comic)

        if len(listContentData) == 0:
            return None

        zipFileCompress = CompressorFileData(
                                filename=directory_name,
                                list_data=listContentData,
                                type='zip',
                                unit=self.unit
                            )
        return zipFileCompress

    def extract_content(
        currentFileZip: CurrentFile,
        password: str = None
    ) -> CurrentFile:
        """
        Must be implemented!.
        """
        pass

    def to_write(
        self,
        currentFileInstance: CurrentFile
    ) -> dict:
        """
        Write data into file.

        Args:
            currentFile: `CurrentFile` instance with data of ZIP or RAR file.

        Returns:
            dict: compressor file information. Keys `'name'`, `'size'`.
        """
        path_file = currentFileInstance.path
        with open(path_file, 'wb') as file:
            file.write(currentFileInstance.bytes_data.getvalue())

        return {
                'name': path_file,
                'size': '%.2f %s' % (
                                currentFileInstance.size,
                                currentFileInstance.unit.upper()
                            )
            }
