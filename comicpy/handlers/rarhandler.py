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

from comicpy.exceptionsClasses import BadPassword

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
        self.number_index = 1

        self.FILE_CBR_ = None
        self.FILE_RAR_ = None
        self.CONVERTED_COMICPY_PATH_ = None

    def reset_names(self) -> None:
        """
        """
        self.FILE_CBR_ = None
        self.FILE_RAR_ = None
        self.CONVERTED_COMICPY_PATH_ = None

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
                # print(rarFileOrigin, rarFileOrigin.filename)
                return rarFileOrigin

        except RarCannotExec as e:
            msg = 'Rar not Installed: \n'
            msg += '%s. Download from "%s"\n' % (e, self.url_page)
            print(msg)
            return -1
        except BadPassword as e:
            print('--> ', e)
            return -1
        except Exception:
            return None

    def to_rar(
        self,
        join: bool,
        converted_comicpy_path: str,
        filenameRAR: str,
        basedir: str,
        data_list: List[CompressorFileData] = None,
    ) -> List[dict]:
        """
        """
        if data_list is None:
            return None

        # Reset names CBR, RAR.
        if join is False:
            self.reset_names()

        name_, extention = self.paths.splitext(
                                self.paths.get_basename(filenameRAR)
                            )

        DIRECTORY_BASE_ = basedir.replace(' ', '_')
        self.CONVERTED_COMICPY_PATH_ = converted_comicpy_path

        # Make directory and save all data into `TEMP` `.RAR_TEMP`
        # id_directory = uuid1().hex
        DIR_RAR_FILES = self.paths.build(
                            self.TEMPDIR,
                            DIRECTORY_BASE_,
                            make=True
                        )
        # print(DIR_RAR_FILES, DIRECTORY_BASE_, self.CONVERTED_COMICPY_PATH_)

        # DELETE THIS
        # join = True  # DELETE THIS
        # DELETE THIS

        ITEM_DIR_ = None
        first_directory = False
        to_rar_directory = {}
        metadata_rar = []

        for data in data_list:
            if join is True:
                if first_directory is False:
                    ITEM_DIR_ = self.paths.get_dirname_level(
                                                data.filename,
                                                level=-1
                                            )
                    first_directory = True
            else:
                ITEM_DIR_ = self.paths.get_dirname_level(
                                            data.filename,
                                            level=-1
                                        )

            if ITEM_DIR_ == '.':
                ITEM_DIR_ = name_

            ITEM_DIR_ = ITEM_DIR_.replace(' ', '_')

            item_filename = self.paths.get_basename(data.filename)
            item_data = data.bytes_data.getvalue()

            DIRECTORY_FILES_ = self.paths.build(
                            DIR_RAR_FILES,
                            ITEM_DIR_,
                            make=True
                        )

            file_path_ = self.paths.build(DIRECTORY_FILES_, item_filename)

            # print(data.filename, item_filename, ITEM_DIR_)
            # print(file_path_, ITEM_DIR_, RAR_FILE_, DIRECTORY_FILES_)

            with open(file_path_, 'wb') as fileImage:
                fileImage.write(item_data)

            if DIRECTORY_FILES_ not in to_rar_directory:
                to_rar_directory[DIRECTORY_FILES_] = ITEM_DIR_

        # print(to_rar_directories)
        # print(converted_comicpy_path, CONVERTED_COMICPY_PATH_)

        for name_dir, rar_name in to_rar_directory.items():
            # print(name_dir, rar_name)

            RAR_NAME_ = '%s.rar'.replace(' ', '_') % (name_dir)
            CBR_NAME_ = '%s.cbr'.replace(' ', '_') % (name_dir)

            if join:
                if self.FILE_RAR_ is None:
                    self.FILE_RAR_ = RAR_NAME_
                    self.FILE_CBR_ = CBR_NAME_
            else:
                self.FILE_RAR_ = RAR_NAME_
                self.FILE_CBR_ = CBR_NAME_

            directory_rar_temp_ = '%s%s' % (
                                        name_dir, self.paths.get_separator()
                                    )

            # print(self.FILE_RAR_, self.FILE_CBR_)

            # Run RAR command
            command = 'rar a -m1 -ep1 -r %s %s' % (
                                    self.FILE_RAR_,
                                    directory_rar_temp_
                                )

            process = subprocess.run(
                args=command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )

            # print('--> retuncode: ', process.returncode)

            if process.returncode == 0:

                metadata_cbr = self.rename_move_rar_cbr(
                                            fileRAR=self.FILE_RAR_,
                                            fileCBR=self.FILE_CBR_
                                        )
                metadata_rar.append(metadata_cbr)

        # Clear Temp Directory and RAR File.
        shutil.rmtree(path=DIR_RAR_FILES)

        return metadata_rar

    def rename_move_rar_cbr(
        self,
        fileRAR: str,
        fileCBR: str
    ) -> None:
        """
        """
        path_CBR_ = None

        destination_path = self.paths.build(
                                self.CONVERTED_COMICPY_PATH_,
                                make=True
                            )
        cbr_name = self.paths.get_basename(fileCBR)
        path_CBR_ = self.paths.build(
                                destination_path,
                                cbr_name
                            )
        metadata = self.get_metadata(path_cbr=fileRAR, final_path=path_CBR_)

        # Rename to RAR to CBR
        shutil.move(src=fileRAR, dst=fileCBR)

        # Move CBR file to `Converted_comicpy`
        try:
            shutil.move(src=fileCBR, dst=destination_path)
        except shutil.Error:
            is_deleted = self.paths.remove(path=path_CBR_)
            if is_deleted:
                shutil.move(src=fileCBR, dst=destination_path)
        return metadata

    def get_metadata(
        self,
        path_cbr: str,
        final_path: str,
    ) -> dict:
        """
        """
        meta = {
                'name': final_path,
                'size': '%.2f %s' % (
                            self.paths.get_size(
                                    path=path_cbr,
                                    unit=self.unit
                            ),
                            self.unit
                    )
            }
        return meta

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
