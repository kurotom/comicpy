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

# from uuid import uuid1
import subprocess
import tempfile
import shutil
import rarfile
from rarfile import (
    PasswordRequired,
    RarCannotExec
)

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
        Resets attributes of instance.
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
            currentFileRar: `CurrentFile` instance with data of original RAR
                            file.
            password: password string of file, default is `None`.
            is_join: boolean if file joining into one, otherwise, no.
            resizeImage: string of size image. Default is `'preserve'`.

        Returns:
            CompressorFileData: instances contains name of directory of images,
                                list of ImageComicData instances, type of
                                compressor.
            int: if password is incorrect.
            None: any other problems.
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
        except Exception as e:
            return None

    def to_rar(
        self,
        join: bool,
        converted_comicpy_path: str,
        pathCBRconverted: str,
        basedir: str,
        data_list: List[CompressorFileData] = None,
        last_item: bool = False
    ) -> List[dict]:
        """
        It groups the raw data into a RAR file and renames it with a CBR
        extension.

        Args
            join: boolean, `True` to join, otherwise, `False`.
            converted_comicpy_path: directory path to all CBR files.
            pathCBRconverted: path of CBR file.
            basedir: name of directory base of CBR file.
            data_list: list of raw data content of RAR file.
            last_item: boolean indicates last item of list of content of RAR
                       file.

        Returns
            list: list of diccionaries with metadata of file/s CBR.
        """
        # print('--> ', pathCBRconverted, converted_comicpy_path, basedir)
        if data_list is None:
            return None

        # Reset names CBR, RAR.
        if join is False:
            self.reset_names()

        name_, extention = self.paths.splitext(
                                self.paths.get_basename(pathCBRconverted)
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

            # print(data, ITEM_DIR_, name_, item_filename)

            DIRECTORY_FILES_ = self.paths.build(
                            DIR_RAR_FILES,
                            ITEM_DIR_,
                            make=True
                        )

            file_path_ = self.paths.build(DIRECTORY_FILES_, item_filename)

            with open(file_path_, 'wb') as fileImage:
                fileImage.write(item_data)

            if DIRECTORY_FILES_ not in to_rar_directory:
                to_rar_directory[DIRECTORY_FILES_] = ITEM_DIR_

        # print(to_rar_directory, DIRECTORY_BASE_, DIR_RAR_FILES)
        # print(converted_comicpy_path, CONVERTED_COMICPY_PATH_)

        for name_dir, rar_name in to_rar_directory.items():
            # print(name_dir, rar_name, pathCBRconverted)

            self.FILE_RAR_ = self.paths.build(
                                    DIR_RAR_FILES,
                                    '%s.rar'.replace(' ', '_') % (name_)
                                )

            directory_rar_temp_ = '%s%s' % (
                                        name_dir,
                                        self.paths.get_separator()
                                    )
            # print(directory_rar_temp_)

            # Run RAR command
            command = 'rar a -r -m1 -ep1 %s %s' % (
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

            if process.returncode != 0:
                return []

        # print(self.FILE_RAR_, name_, DIR_RAR_FILES)
        self.FILE_CBR_ = self.paths.build(
                                DIR_RAR_FILES,
                                '%s.cbr' % (name_)
                            )
        # print(self.FILE_CBR_, self.FILE_RAR_, self.CONVERTED_COMICPY_PATH_)

        if join:
            if last_item:
                metadata_cbr = self.rename_move_rar_cbr(
                                            fileRAR=self.FILE_RAR_,
                                            fileCBR=self.FILE_CBR_,
                                            directory_files=DIR_RAR_FILES
                                        )
                metadata_rar.append(metadata_cbr)
        else:
            metadata_cbr = self.rename_move_rar_cbr(
                                            fileRAR=self.FILE_RAR_,
                                            fileCBR=self.FILE_CBR_,
                                            directory_files=DIR_RAR_FILES
                                        )
            metadata_rar.append(metadata_cbr)

        return metadata_rar

    def rename_move_rar_cbr(
        self,
        fileRAR: str,
        fileCBR: str,
        directory_files: str
    ) -> None:
        """
        Rename and move file CBR to destination.

        Args
            fileRAR: path of RAR file.
            fileCBR: path of CBR file.
            directory_files: main directory of content of RAR file.

        Returns
            dict: directory with name and size of file.
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

        # metadata of CBR
        metadata = super().get_metadata(path=path_CBR_)

        # Rename to RAR to CBR
        shutil.move(src=fileRAR, dst=fileCBR)

        # Move CBR file to `Converted_comicpy`
        try:
            shutil.move(src=fileCBR, dst=destination_path)
        except shutil.Error:
            is_deleted = self.paths.remove(path=path_CBR_)
            if is_deleted:
                shutil.move(src=fileCBR, dst=destination_path)

        # Clear Temp Directory and RAR File.
        shutil.rmtree(path=directory_files)

        return metadata

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
