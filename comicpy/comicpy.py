# -*- coding: utf-8 -*-
"""
"""


from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData
)

from comicpy.checkfile import CheckFile

from comicpy.exceptionsClasses import (
    InvalidFile,
    EmptyFile,
    FileExtentionNotMatch,
    DirectoryPathNotExists,
    DirectoryEmptyFilesValid,
    DirectoryFilterEmptyFiles
)

from comicpy.valid_extentions import (
    pdfFileExtention,
    comicFilesExtentions,
    compressorsExtentions,
    imagesExtentions,
    validExtentionsList
)

from comicpy.handlers import (
    PdfHandler,
    ZipHandler,
    RarHandler
)

import io
import glob
import os

from typing import List, TypeVar, Union, NewType

RAR = TypeVar('rar')
ZIP = TypeVar('zip')

RarBytesIO = TypeVar('RarBytesIO')
ZipBytesIO = TypeVar('ZipBytesIO')

FileNameCBZ = TypeVar('FileNameCBZ')
CurrentFileZip = TypeVar('CurrentFileZip')
CurrentFileRar = TypeVar('CurrentFileRar')

PDFEXT = TypeVar('pdf')
CBZEXT = TypeVar('cbz')
CBREXT = TypeVar('cbr')


class ComicPy:

    def __init__(
        self,
        file_path: str = None
    ) -> None:
        self.directory_path = None
        self.filename = file_path
        self.currentFile = self.read(filename=self.filename)
        self.checker = CheckFile()
        self.ziphandler = ZipHandler()
        self.pdfphandler = PdfHandler()
        self.rarhandler = RarHandler()

    def read(
        self,
        filename: str
    ) -> None:
        """
        """
        if filename is None:
            return None
        with open(filename, 'rb') as file:
            file.seek(0)
            data = file.read()
            if len(data) == 0:
                file.close()
                raise EmptyFile()

            currentFile = CurrentFile(
                            filename=filename,
                            bytes_data=io.BytesIO(data),
                            chunk_bytes=data[:8]
                        )
        return currentFile

    def check_file(
        self,
        currentFile: CurrentFile
    ) -> bool:
        is_valid = self.checker.check(currenf_file=currentFile)
        # print('-> check_file ', is_valid)
        if is_valid is False:
            raise FileExtentionNotMatch()
        elif is_valid is None:
            raise InvalidFile()
        else:
            return is_valid

    def raiser_error_compressor(
        self,
        compressor_str: str,
    ) -> None:
        compressors = [
                        i.replace('.', '')
                        for i in list(compressorsExtentions.values())
                    ]
        if compressor_str not in compressors:
            msg = 'Must be `rar` or `zip` for compressor parameter.'
            raise ValueError(msg)

    def process_pdf(
        self,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[RarBytesIO, ZipBytesIO]:
        compressor = compressor.replace('.', '').lower().strip()

        self.raiser_error_compressor(compressor_str=compressor)

        self.check_file(currentFile=self.currentFile)

        listImagesPDF = self.pdfphandler.process_pdf(
                            currentFilePDF=self.currentFile
                        )
        compressFileData = CompressorFileData(
                    filename=self.currentFile.name.replace(' ', '_'),
                    list_data=listImagesPDF,
                    type=compressor
                )
        compressFileData.setExtention()

        compressedCurrentFileIO = self.to_compressor(
                            dataRawFile=compressFileData,
                            compressor=compressor
                        )
        compressedCurrentFileIO.name = self.currentFile.name

        return compressedCurrentFileIO

    def process_zip(
        self,
    ) -> Union[RarBytesIO, ZipBytesIO]:

        self.check_file(currentFile=self.currentFile)

        dataZipIO = self.ziphandler.rename_zip_cbz(
                                currentFileZip=self.currentFile
                            )
        return dataZipIO

    def process_rar(
        self,
    ) -> Union[RarBytesIO, ZipBytesIO]:

        self.check_file(currentFile=self.currentFile)

        dataRarIO = self.rarhandler.rename_rar_cbr(
                                currentFileRar=self.currentFile
                            )
        return dataRarIO


    def process_dir(
        self,
        directory_path: str,
        extention_filter: Union[PDFEXT, CBZEXT, CBREXT],  # 'pdf', 'cbz', 'cbr'
        filename: str = None,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[CompressorFileData, None]:
        compressor = compressor.replace('.', '').lower().strip()

        if extention_filter not in validExtentionsList:
            raise ValueError('Extention not valid!.')

        self.raiser_error_compressor(compressor_str=compressor)

        dir_abs_path = os.path.abspath(directory_path)
        if not os.path.exists(dir_abs_path):
            raise DirectoryPathNotExists(dir_path=directory_path)

        self.directory_path = directory_path

        pattern = '*.%s' % (extention_filter)
        filesMatch = glob.glob(pathname=pattern, root_dir=self.directory_path)

        filesMatch.sort()

        if len(filesMatch) == 0:
            raise DirectoryFilterEmptyFiles(
                            dir_path=self.directory_path,
                            filter=extention_filter
                        )
        elif len(filesMatch) > 0:
            list_filePaths = [
                                os.path.join(self.directory_path, item)
                                for item in filesMatch
                            ]

            # list_currentFiles = []
            list_CompressorsModel = []
            for item_path in list_filePaths:
                if os.path.exists(item_path):

                    fileCurrentData = self.read(filename=item_path)
                    # print('-> ', fileCurrentData, fileCurrentData.extention)

                    self.check_file(currentFile=fileCurrentData)

                    extention = fileCurrentData.extention
                    filenameCurrent = fileCurrentData.name.replace(' ', '_')
                    # print(fileCurrentData.bytes_data.getbuffer().nbytes)

                    if extention == '.pdf':
                        # print('>> DIR PDF')
                        listImagesPDF = self.pdfphandler.process_pdf(
                                            currentFilePDF=fileCurrentData
                                        )
                        compressFileData = CompressorFileData(
                                    filename=filenameCurrent,
                                    list_data=listImagesPDF,
                                    type=compressor
                                )
                        compressFileData.setExtention()
                        list_CompressorsModel.append(compressFileData)

                    elif extention == '.zip' or extention == '.cbz':
                        # print('>> DIR ZIP')
                        compressFileData = self.ziphandler.extract_images(
                                            currentFileZip=fileCurrentData
                                        )
                        list_CompressorsModel.append(compressFileData)

                    elif extention == '.rar' or extention == '.cbr':
                        print('>> DIR RAR')
                        listImageComicDataRar = self.rarhandler.extract_images(
                                            currentFileRar=fileCurrentData
                                        )
                        list_CompressorsModel.append(listImageComicDataRar)

            if filename is None:
                filenameCompressor = os.path.basename(
                                                self.directory_path
                                            )
            else:
                filenameCompressor = filename

            compressedCurrentFileIO = self.to_compressor(
                                filename=filenameCompressor,
                                dataRawFile=list_CompressorsModel,
                                compressor=compressor
                            )
            return compressedCurrentFileIO

    def to_compressor(
        self,
        filename: str,
        dataRawFile: List[CompressorFileData],
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[CompressorFileData, None]:
        if type(dataRawFile) is not list:
            dataRawFile = [dataRawFile]

        if compressor == 'zip':
            compressorFile = self.ziphandler.to_zip(
                                filenameZIP=filename,
                                listZipFileCompress=dataRawFile
                            )
        elif compressor == 'rar':
            compressorFile = self.rarhandler.to_rar(
                                filenameRAR=filename,
                                listRarFileCompress=dataRawFile
                            )

        if compressorFile is None:
            return None

        compressorFile.name = filename

        return compressorFile

    def write_cbz(
        self,
        currentFileZip: CurrentFileZip
    ) -> dict:
        if currentFileZip.extention is None or currentFileZip.extention == '':
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
        filename: str,
        show: bool = True
    ) -> bool:
        fileCompressed = self.read(filename=filename)
        is_valid = self.checker.check(currenf_file=fileCompressed)
        if show:
            string = 'File is valid?:  "%s"' % (is_valid)
            print(string)
        return is_valid
