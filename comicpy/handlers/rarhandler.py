# -*- coding: utf-8 -*-
"""
Handler related to files RAR.

Temporary data written in TEMP directory.

Rar executable path must be in `PATH` environment variable.
"""

from comicpy.handlers.imageshandler import ImagesHandler
from comicpy.utils import Paths

from comicpy.models import (
    CurrentFile,
    CompressorFileData
)

from comicpy.handlers.baseziprar import BaseZipRarHandler

from comicpy.valid_extentions import ValidExtentions

from uuid import uuid1
import subprocess
import tempfile
import shutil
import rarfile
from rarfile import (
    PasswordRequired,
    RarCannotExec
)

import io

from typing import List, Union, TypeVar

PRESERVE = TypeVar('preserve')
SMALL = TypeVar('small')
MEDIUM = TypeVar('medium')
LARGE = TypeVar('large')


class RarHandler(BaseZipRarHandler):
    """
    Class in charge of extract images, rename file RAR, create RAR file, write
    data into RAR file.
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
        self.type = 'rar'
        self.imageshandler = ImagesHandler()
        self.validextentions = ValidExtentions()
        self.paths = Paths()
        self.url_page = 'https://www.rarlab.com/download.htm'
        self.number_index = 0

    def testRar(
        self,
        currentFileRar: CurrentFile
    ) -> None:
        """
        Checks if RAR file is password protected.

        Args:
            currentFileRar: `CurrentFile` instance with raw data of file RAR.

        Returns:
            bool: `True` if password protected, otherwise, retuns `False`.
        """
        try:
            with rarfile.RarFile(
                file=currentFileRar.bytes_data,
                mode='r'
            ) as rarFile:
                f = rarFile.namelist()[:1]
                rarFile.read(f[0])
            return False
        except rarfile.RarCannotExec:
            return None
        except PasswordRequired:
            return True

    def extract_content(
        self,
        currentFileRar: CurrentFile,
        password: str = None,
        is_join: bool = False,
        resizeImage: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[CompressorFileData, None, int]:
        """
        Extract images from RAR file.

        Args:
            currentFile: `CurrentFile` instance with data of original RAR file.
            password: password string of file, default is `None`.
            imageSize: string of size image. Default is `'small'`.

        Returns:
            CompressorFileData: instances contains name of directory of images,
                                list of ImageComicData instances, type of
                                compressor.
        """
        rawDataRar = currentFileRar.bytes_data

        try:
            with rarfile.RarFile(
                file=rawDataRar,
                mode='r'
            ) as rar_file:

                rarFileOrigin = super().iterateFiles(
                    instanceCompress=rar_file,
                    password=password,
                    resize=resizeImage,
                    type_compress='rar',
                    join=is_join
                )

                if rarFileOrigin is not None:
                    if rarFileOrigin.filename == '':
                        rarFileOrigin.filename = currentFileRar.name

                return rarFileOrigin

        except RarCannotExec as e:
            msg = 'Rar not Installed: \n'
            msg += '%s. Download from "%s"\n' % (e, self.url_page)
            print(msg)
            return -1
        except:
            return None

    def to_rar(
        self,
        listRarFileCompress: List[CompressorFileData],
        join: bool,
        filenameRAR: str = None,
    ) -> Union[List[CurrentFile], None]:
        """
        Handles how the data in the RAR file(s) should be written.

        Args:
            listRarFileCompress: list of `CompressorFileData` instances.
            filenameRAR: name of the RAR archive.
            join: if `True` merge all files, otherwise, no.

        Returns:
            List[CurrentFile]: list of `CurrentFile` instances contains bytes
                               of the RAR files.
            None: if `subprocess.run` fails.
        """
        # print(listRarFileCompress)
        if len(listRarFileCompress) == 0:
            return None

        data_of_rars = []
        if join is True:
            currentFileRar = self.__to_rar_data(
                    listRarFileCompress=listRarFileCompress,
                    filenameRar=filenameRAR
                )
            data_of_rars.append(currentFileRar)
        elif join is False:
            for file in listRarFileCompress:
                current_file_list = [file]
                currentFileRar = self.__to_rar_data(
                        listRarFileCompress=current_file_list,
                        filenameRar=file.filename
                    )
                data_of_rars.append(currentFileRar)

        return data_of_rars

    def __to_rar_data(
        self,
        listRarFileCompress: List[CompressorFileData],
        filenameRar: str = None,
    ) -> CurrentFile:
        """
        Write data of `CompressorFileData` into RAR file.

        Args:
            listRarFileCompress: list of `CompressorFileData` instances with
                                 RAR compressor data.
            filenameRar: name of file RAR.

        Returns:
            CurrentFile: with data of RAR file.
        """
        if filenameRar is None:
            filenameRar = 'FileRar'

        buffer_dataRar = io.BytesIO()

        id_directory = uuid1().hex

        # Make directory and save all data into `TEMP` `.RAR_TEMP`
        ROOT_PATH = self.paths.build(self.TEMPDIR, id_directory)
        DIR_RAR_FILES = self.paths.build(
                            ROOT_PATH, filenameRar,
                            make=True
                        )
        RAR_FILE_ = self.paths.build(DIR_RAR_FILES) + '.rar'
        # print(ROOT_PATH)

        for item in listRarFileCompress:
            # print(item, len(item.list_data), item.filename)
            directory_path = self.paths.build(
                                    DIR_RAR_FILES, item.filename,
                                    make=True
                                )

            for image in item.list_data:
                file_name = self.paths.get_basename(image.filename)
                image_path = self.paths.build(directory_path, file_name)

                data = image.bytes_data.getvalue()
                with open(image_path, 'wb') as fileImage:
                    fileImage.write(data)

        # Run RAR command
        command = 'rar a -m1 -ep1 -r %s %s/' % (
                                RAR_FILE_,
                                DIR_RAR_FILES
                            )
        process = subprocess.run(
            args=command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        # print('--> retuncode: ', process.returncode)

        if process.returncode == 0:

            # Load RAR into io.BytesIO
            with open(RAR_FILE_, 'rb') as file_rar:
                shutil.copyfileobj(fsrc=file_rar, fdst=buffer_dataRar)

            # Clear Temp Directory and RAR File.
            shutil.rmtree(path=ROOT_PATH)

            rarFileCurrent = CurrentFile(
                                filename=filenameRar,
                                bytes_data=buffer_dataRar,
                                unit=self.unit,
                                extention='.cbr'
                            )
            return rarFileCurrent

        else:
            return None

    def to_write(
        self,
        currentFileRar: CurrentFile
    ) -> List[dict]:
        """
        Send data to `BaseZipRarHandler.to_write()` to save the RAR file data.

        Args:
            currentFileRar: `CompressorFileData` instance, contains data of
                            RAR file.

        Returns:
            List[dict]: list of dicts with information of all files saved.
                        'name': path to the file.
                        'size': size of file.
        """
        return super().to_write(currentFileInstance=currentFileRar)
