# -*- coding: utf-8 -*-
"""
In charge of managing the workflow between handlers and files or directories
given by the user.

The flow consists of giving a PDF file or directory and storing the images it
contains in CBR or CBZ files.
"""


from comicpy.models import (
    CurrentFile,
    CompressorFileData
)

from comicpy.checkfile import CheckFile
from comicpy.utils import Paths

from comicpy.exceptionsClasses import (
    InvalidFile,
    EmptyFile,
    FileExtentionNotMatch,
    DirectoryPathNotExists,
    DirectoryFilterEmptyFiles,
    UnitFileSizeInvalid
)

from comicpy.valid_extentions import (
    compressorsExtentions,
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

from typing import List, TypeVar, Union


RAR = TypeVar('rar')
ZIP = TypeVar('zip')

PDFEXT = TypeVar('pdf')
CBZEXT = TypeVar('cbz')
CBREXT = TypeVar('cbr')


class ComicPy:
    """
    Class in charge of manipulating the workflow, loading data from file(s),
    verifying, extracting images, saving to final `CBZ` or `CBR` file.
    """

    def __init__(
        self,
        unit: str = 'mb'
    ) -> None:
        """
        Constructor.

        Args:
            unit: indicate unit of measure using to represent file size.
        """
        self.unit = self.__validating_unit(unit=unit)
        self.directory_path = None
        self.filename = None
        self.currentFile = None
        self.checker = CheckFile()
        self.ziphandler = ZipHandler(unit=self.unit)
        self.pdfphandler = PdfHandler(unit=self.unit)
        self.rarhandler = RarHandler(unit=self.unit)
        self.paths = Paths()

    def __validating_unit(
        self,
        unit: str
    ) -> None:
        """
        Validating unit measure.

        Args:
            unit: str -> indicate unit of measure using to represent file size.

        Returns:
            str: unit validated.

        Raises:
            UnitFileSizeInvalid: if "unit" given is not valid.
        """
        units = ("b", "kb", "mb", "gb")
        unit = unit.lower()
        if unit not in units:
            raise UnitFileSizeInvalid()
        return unit

    def read(
        self,
        filename: str
    ) -> CurrentFile:
        """
        Read content of file.

        Args:
            filename: str -> file name.

        Returns:
            Returns `CurrentFile` object with data of file.

        Raises:
            EmptyFile: if file is empty.
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
                            chunk_bytes=data[:8],
                            unit=self.unit
                        )
        return currentFile

    def check_file(
        self,
        currentFile: CurrentFile
    ) -> bool:
        """
        Check file if is valid exploring file signature of file.

        Args:
            currentFile: `CurrentFile` instance of a file.

        Returns:
            bool: boolean if file is valid (True) or not (False).

        Raises:
            FileExtentionNotMatch: if file extention of file is not valid.
            InvalidFile: if file extention and file signature not match.
        """
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
        """
        Check compressor extention given.

        Args:
            compressor_str: str -> string of compressor to use.

        Raises:
            ValueError: if `compressor_str` is not valid.
        """
        compressors = [
                        i.replace('.', '')
                        for i in list(compressorsExtentions.values())
                    ]
        if compressor_str not in compressors:
            msg = 'Must be `rar` or `zip` for compressor parameter.'
            raise ValueError(msg)

    def load_file(
        self,
        filename: str
    ) -> None:
        """
        Load file given, sets attributes `filename`, `currentFile`.
        """
        self.filename = filename
        self.currentFile = self.read(filename=self.filename)

    def process_pdf(
        self,
        filename: str,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> CompressorFileData:
        """
        Process PDF file, load content, extract images.

        Args:
            filename: str -> PDF file name.

        Returns:
            CompressorFileData: instance representing the compressor file,
                                contains image data (bytes), image name, type
                                of compressor used.
        """

        self.load_file(filename=filename)

        compressor = compressor.replace('.', '').lower().strip()

        self.raiser_error_compressor(compressor_str=compressor)

        self.check_file(currentFile=self.currentFile)

        listImagesPDF = self.pdfphandler.process_pdf(
                            currentFilePDF=self.currentFile
                        )
        compressFileData = CompressorFileData(
                    filename=self.currentFile.name.replace(' ', '_'),
                    list_data=listImagesPDF,
                    type=compressor,
                    unit=self.unit
                )
        compressFileData.setExtention()

        compressedCurrentFileIO = self.to_compressor(
                            filename=compressFileData.filename,
                            dataRawFile=compressFileData,
                            compressor=compressor,
                            join_files=False
                        )
        compressedCurrentFileIO.name = self.currentFile.name

        return compressedCurrentFileIO

    def process_zip(
        self,
        filename: str
    ) -> CurrentFile:
        """
        Process ZIP files.

        Args:
            filename: str -> ZIP file name.

        Returns:
            CurrentFile: instance representing the data of the ZIP file named
                         CBZ.
        """

        self.load_file(filename=filename)

        self.check_file(currentFile=self.currentFile)

        zipCompressorFileData = self.ziphandler.rename_zip_cbz(
                                currentFileZip=self.currentFile
                            )
        return zipCompressorFileData

    def process_rar(
        self,
        filename: str
    ) -> CurrentFile:
        """
        Process RAR files.

        Args:
            filename: str -> RAR file name.

        Returns:
            CurrentFile: the instance represents the data of the RAR archive
                         with the name CBR
        """

        self.load_file(filename=filename)

        self.check_file(currentFile=self.currentFile)

        rarCompressorFileData = self.rarhandler.rename_rar_cbr(
                                currentFileRar=self.currentFile
                            )
        return rarCompressorFileData

    def process_dir(
        self,
        directory_path: str,
        extention_filter: Union[PDFEXT, CBZEXT, CBREXT],  # 'pdf', 'cbz', 'cbr'
        filename: str = None,
        password: str = None,
        compressor: Union[RAR, ZIP] = 'zip',
        join: bool = False
    ) -> Union[CompressorFileData, None]:
        """
        Searches files in the given directory, searches only PDF, CBZ, CBR
        files.
        By default, all files are sorted alphanumerically.

        Args:
            directory_path: directory name.
            extention_filter: ['pdf', 'cbz', 'cbr'] -> extension of the file to
                                                       search in the directory.
            filename: output file name.
            compressor: ['zip', 'rar'] -> extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            password: password string of file, default is `None`.

        Returns:
            CompressorFileData: the instance represents the data of the RAR or
                                ZIP compressor file used.
            None: if the list of images is empty, the file has no images.

        Raises:
            ValueError: if the extension used to filter the files is not valid.
            DirectoryPathNotExists: if the directory path does not exist.
            DirectoryFilterEmptyFiles: if no file matches the filter file
                                       extension.
        """
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
                                    type=compressor,
                                    unit=self.unit
                                )
                        compressFileData.setExtention()
                        list_CompressorsModel.append(compressFileData)

                    elif extention == '.zip' or extention == '.cbz':
                        # print('>> DIR ZIP')
                        compressFileData = self.ziphandler.extract_images(
                                            currentFileZip=fileCurrentData,
                                            password=password
                                        )
                        list_CompressorsModel.append(compressFileData)

                    elif extention == '.rar' or extention == '.cbr':
                        # print('>> DIR RAR')
                        compressorFileData = self.rarhandler.extract_images(
                                            currentFileRar=fileCurrentData,
                                            password=password
                                        )
                        list_CompressorsModel.append(compressorFileData)

            if filename is None:
                filenameCompressor = os.path.basename(
                                                self.directory_path
                                            )
            else:
                filenameCompressor = filename

            compressedCurrentFileIO = self.to_compressor(
                                filename=filenameCompressor,
                                dataRawFile=list_CompressorsModel,
                                compressor=compressor,
                                join_files=join
                            )
            return compressedCurrentFileIO

    def to_compressor(
        self,
        dataRawFile: List[CompressorFileData],
        join_files: bool,
        filename: str = None,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> Union[CompressorFileData, None]:
        """
        Convert data of list of CompressorFileData to only RAR or ZIP file.

        Args:
            dataRawFile: list of CompressorFileData instances, this class
                         contains image list data, filename, etc.
            filename: name of the output file.
            compressor: ['rar', 'zip'], by default `zip`, compressor to use.

        Returns:
            CompressorFileData: instance represents the data of the RAR or ZIP
                                compressor file used.
            None: if the list of images is empty, the file has no images.
        """
        if type(dataRawFile) is not list:
            dataRawFile = [dataRawFile]

        if compressor == 'zip':
            compressorFile = self.ziphandler.to_zip(
                                filenameZIP=filename,
                                listZipFileCompress=dataRawFile,
                                join=join_files
                            )
        elif compressor == 'rar':
            compressorFile = self.rarhandler.to_rar(
                                filenameRAR=filename,
                                listRarFileCompress=dataRawFile,
                                join=join_files
                            )

        if compressorFile is None:
            return None

        return compressorFile

    def write_cbz(
        self,
        currentFileZip: CompressorFileData,
        path: str = '.'
    ) -> dict:
        """
        Write data of currentFileZip instance.

        Args:
            currentFileZip: instance with the data to create and save in a ZIP
                            file.
            path: location where the CBZ file will be stored. Default `'.'`.
        Returns:
            dict: ZIP file information.
        """
        save_path = self.paths.build(path, currentFileZip.filename)
        infoFileZip = self.ziphandler.to_write(
                            currentFileZip=currentFileZip,
                            path_dest=save_path
                        )
        # print(infoFileZip)
        return infoFileZip

    def write_cbr(
        self,
        currentFileRar: CompressorFileData,
        path: str = '.'
    ) -> dict:
        """
        Write data of currentFileRar instance.

        Args:
            currentFileRar: instance with the data to create and save in a RAR
                            file.
            path: location where the CBR file will be stored. Default `'.'`.
        Returns:
            dict: RAR file information, keys: "name", "size".
        """
        save_path = self.paths.build(path, currentFileRar.filename)
        infoFileRar = self.rarhandler.to_write(
                            currentFileRar=currentFileRar,
                            path_dest=save_path
                        )
        # print(infoFileRar)
        return infoFileRar

    def check_integrity(
        self,
        filename: str,
        show: bool = True,
    ) -> bool:
        """
        Checks if the output archive (RAR or ZIP) is valid, looking for its
        file signatures.

        Args:
            filename: ZIP or RAR output file name, given of method `write_cbr`
                      or `write_cbz`.
            show: boolean to print on terminal. Default is `True`.
        """
        fileCompressed = self.read(filename=filename)
        is_valid = self.checker.check(currenf_file=fileCompressed)
        if show:
            string = 'File is valid?:  "%s"' % (is_valid)
            print(string)
        return is_valid

    def __str__(self) -> str:
        """
        Representation of class.

        Returns:
            str: information of instance, Name and parameters used.
        """
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Representation of class.

        Returns:
            str: information of instance, Name and parameters used.
        """
        return '<[Class: "%s", Parameters: "%s"]>' % (
                        type(self).__name__,
                        self.unit
                    )
