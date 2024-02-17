# -*- coding: utf-8 -*-
"""
"""


from comicpy.models import (
    ImageComicData,
    CurrentFile
)
from comicpy.checkfile import CheckFile
from comicpy.exceptionsClasses import (
    InvalidFile,
    EmptyFile,
    FileExtentionNotMatch,
    DirectoryPathNotExists,
    DirectoryEmptyFilesValid
)

from comicpy.handlers import (
    PdfHandler,
    ZipHandler,
    RarHandler
)

import io
import glob
import os

from typing import List, TypeVar, Union

RAR = TypeVar('rar')
ZIP = TypeVar('zip')

RarBytesIO = TypeVar('RarBytesIO')
ZipBytesIO = TypeVar('ZipBytesIO')

FileNameCBZ = TypeVar('FileNameCBZ')
CurrentFileZip = TypeVar('CurrentFileZip')
CurrentFileRar = TypeVar('CurrentFileRar')


class ComicPy:

    def __init__(
        self,
        pdf_path: str
    ) -> None:
        self.filename = pdf_path
        self.currentFile = self.read()
        self.read()
        self.checker = CheckFile()
        self.ziphandler = ZipHandler()
        self.pdfphandler = PdfHandler()
        self.rarhandler = RarHandler()

    def read(self) -> None:
        """
        """
        with open(self.filename, 'rb') as file:
            file.seek(0)
            data = file.read()
            if len(data) == 0:
                file.close()
                raise EmptyFile()

            currentFile = CurrentFile(
                            filename=self.filename,
                            bytes_data=io.BytesIO(data),
                            chunk_bytes=data[:8]
                        )
        return currentFile

    def check_file(self) -> bool:
        is_valid = self.checker.check(currenf_file=self.currentFile)
        print(is_valid)
        if is_valid is False:
            raise FileExtentionNotMatch()
        elif is_valid is None:
            raise InvalidFile()
        else:
            return is_valid

    def raiser_error_compressor(
        self,
        compressor_str: str
    ) -> None:
        compressors = 'zip', 'rar'
        if compressor_str not in compressors:
            msg = 'Must be `rar` or `zip` for compressor parameter.'
            raise ValueError(msg)

    def process_pdf(
        self,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[RarBytesIO, ZipBytesIO]:
        self.raiser_error_compressor(compressor_str=compressor)

        self.check_file()

        listImagesRawIO = self.pdfphandler.process_pdf(
                            currentFilePDF=self.currentFile
                        )
        zipCurrentFileIO = self.to_compressor(
                            dataRawFile=listImagesRawIO,
                            compressor=compressor
                        )
        zipCurrentFileIO.filename = self.currentFile.name
        return zipCurrentFileIO

    def process_zip(
        self,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[RarBytesIO, ZipBytesIO]:
        self.raiser_error_compressor(compressor_str=compressor)

        self.check_file()

        dataZipIO = self.ziphandler.rename_zip_cbz(
                                currentFileZip=self.currentFile
                            )
        return dataZipIO

    def process_rar(
        self,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[RarBytesIO, ZipBytesIO]:
        self.raiser_error_compressor(compressor_str=compressor)

        self.check_file()

        dataRarIO = self.rarhandler.rename_rar_cbr(
                                currentFileRar=self.currentFile
                            )
        return dataRarIO



    def process_dir(
        self,
        directory_path: str,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[RarBytesIO, ZipBytesIO]:
        self.raiser_error_compressor(compressor_str=compressor)

        # self.check_file()

        dir_abs_path = os.path.abspath(directory_path)
        if not os.path.exists(dir_abs_path):
            raise DirectoryPathNotExists(dir_path=directory_path)

        print(glob.glob('*.cbz', root_tid=dir_abs_path))








    def to_compressor(
        self,
        dataRawFile: io.BytesIO,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> CurrentFileZip:
        if compressor == 'zip':
            zip_file_compress = self.ziphandler.to_zip(
                                listImageComicData=dataRawFile
                            )
            return zip_file_compress

        elif compressor == 'rar':
            rar_file_compress = self.rarhandler.to_rar(
                                listImageComicData=dataRawFile
                            )
            return rar_file_compress

    def write_cbz(
        self,
        currentFileZip: CurrentFileZip
    ) -> dict:
        currentFileZip.extention = '.cbz'
        infoFileZip = self.ziphandler.to_write(
                            currentFileZip=currentFileZip
                        )
        # print(infoFileZip)
        return infoFileZip

    def write_cbr(
        self,
        currentFileRar: CurrentFileRar
    ) -> dict:
        currentFileRar.extention = '.cbr'
        infoFileRar = self.rarhandler.to_write(
                            currentFileRar=currentFileRar
                        )
        # print(infoFileZip)
        return infoFileRar

    def check_integrity(
        self,
        filename: str
    ) -> bool:
        fileCompressed = self.read()
        is_valid = self.checker.check(currenf_file=fileCompressed)
        return is_valid
