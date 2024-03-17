# -*- coding: utf-8 -*-
"""
In charge of managing the workflow between handlers and files or directories
given by the user.

The flow consists of giving a PDF file or directory and storing the images it
contains in CBR or CBZ files.

The default directory to save all converted files is `Converted_comicpy`, using
the current location when running this program.
"""


from comicpy.models import (
    CurrentFile,
    CompressorFileData
)

from comicpy.checkfile import CheckFile
from comicpy.utils import (
    Paths,
    VarEnviron
)

from comicpy.exceptionsClasses import (
    InvalidFile,
    EmptyFile,
    FileExtentionNotMatch,
    DirectoryPathNotExists,
    DirectoryFilterEmptyFiles,
    UnitFileSizeInvalid,
    FilePasswordProtected
)

from comicpy.valid_extentions import ValidExtentions

from comicpy.handlers import (
    PdfHandler,
    ZipHandler,
    RarHandler,
    DirectoryHandler
)

import io

from typing import List, TypeVar, Union


IMAGES = TypeVar('images')
RAR = TypeVar('rar')
ZIP = TypeVar('zip')
PDF = TypeVar('pdf')
CBZ = TypeVar('cbz')
CBR = TypeVar('cbr')

PRESERVE = TypeVar('preserve')
SMALL = TypeVar('small')
MEDIUM = TypeVar('medium')
LARGE = TypeVar('large')


class ComicPy:
    """
    Class in charge of manipulating the workflow, loading data from file(s),
    verifying, extracting images, saving to final `CBZ` or `CBR` file.
    """
    PREFIX_CONVERTED = 'Converted_comicpy'

    def __init__(
        self,
        unit: str = 'mb',
        exec_path_rar: str = None,
        show_progress: bool = False
    ) -> None:
        """
        Constructor.

        Args:
            unit: indicate unit of measure using to represent file size.
        """
        VarEnviron.setup(path_exec=exec_path_rar)
        self.unit = self.__validating_unit(unit=unit)
        self.show_progress = show_progress
        self.directory_path = None
        self.filename = None
        self.currentFile = None
        self.checker = CheckFile()
        self.directoryhandler = DirectoryHandler(unit=self.unit)
        self.ziphandler = ZipHandler(unit=self.unit)
        self.pdfphandler = PdfHandler(unit=self.unit)
        self.rarhandler = RarHandler(unit=self.unit)
        self.paths = Paths()
        self.validextentions = ValidExtentions()

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
                    for i in self.validextentions.get_compressors_extentions()
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

    def check_protectedFile(
        self,
        handler: Union[RarHandler, ZipHandler],
        compressCurrentFile: CurrentFile,
        password: str = None
    ) -> bool:
        """
        Checks if file Rar or Zip is protected with password. If `True` and
        `password` is `None` raises `ZipFilePasswordProtected`.

        Args:
            handler: handler instance of `RarHandler` or `ZipHandler`.
            compressCurrentFile: `CurrentFile` instance.
            password: password of file ZIP or RAR.

        Returns
            bool: `True` if is protected, otherwise, `False`.

        Raises
            FilePasswordProtected: if `password` parameters and `is_protected`
                                   are `True`s.
        """
        if handler.type == ValidExtentions.ZIP[1:]:
            is_protected = handler.testZip(currentFileZip=compressCurrentFile)
        if handler.type == ValidExtentions.RAR[1:]:
            is_protected = handler.testRar(currentFileRar=compressCurrentFile)
        if is_protected and password is None:
            msg = 'File %s is protected with password.\n' % (
                                handler.type.upper()
                            )
            raise FilePasswordProtected(message=msg)
        elif is_protected and password is not None:
            return True
        return False

    def process_pdf(
        self,
        filename: str,
        compressor: Union[RAR, ZIP] = 'zip',
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> List[CurrentFile]:
        """
        Process PDF file, load content, extract images.

        Args:
            filename: str -> PDF file name.

        Returns:
            CompressorFileData: instance representing the compressor file,
                                contains image data (bytes), image name, type
                                of compressor used.
        """
        self.__show_progress(file=filename)

        self.load_file(filename=filename)

        compressor = compressor.replace('.', '').lower().strip()

        self.raiser_error_compressor(compressor_str=compressor)

        self.check_file(currentFile=self.currentFile)

        compressFileData = self.pdfphandler.process_pdf(
                            currentFilePDF=self.currentFile,
                            compressor=compressor,
                            resizeImage=resize
                        )
        if compressFileData is None:
            raise EmptyFile('File PDF not have images.')

        compressedCurrentFileIO = self.to_compressor(
                            filename=compressFileData.filename,
                            listCompressorData=compressFileData,
                            compressor=compressor,
                            join_files=False
                        )
        return compressedCurrentFileIO

    def process_zip(
        self,
        filename: str,
        password: str = None,
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[List[CurrentFile], None]:
        """
        Process ZIP files.

        Args:
            filename: str -> ZIP file name.

        Returns:
            CurrentFile: instance representing the data of the ZIP file named
                         CBZ.
        """
        self.__show_progress(file=filename)

        self.load_file(filename=filename)

        self.check_file(currentFile=self.currentFile)

        self.check_protectedFile(
                handler=self.ziphandler,
                compressCurrentFile=self.currentFile,
                password=password
            )
        zipCompressorFileData = self.ziphandler.extract_content(
                                    currentFileZip=self.currentFile,
                                    password=password,
                                    resizeImage=resize
                                )

        if zipCompressorFileData is None:
            msg = 'ZIP not have images.'
            exts = self.validextentions.get_container_valid_extentions()
            msg += 'Valid Extentions:  ' + ', '.join(exts) + '\n'
            raise EmptyFile(msg)

        compressedCurrentFileIO = self.to_compressor(
                            filename=zipCompressorFileData.filename,
                            listCompressorData=[zipCompressorFileData],
                            compressor='zip',
                            join_files=False
                        )
        return compressedCurrentFileIO

    def process_rar(
        self,
        filename: str,
        password: str = None,
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[List[CurrentFile], None]:
        """
        Process RAR files.

        Args:
            filename: str -> RAR file name.

        Returns:
            CurrentFile: the instance represents the data of the RAR archive
                         with the name CBR
        """
        self.__show_progress(file=filename)

        self.load_file(filename=filename)

        self.check_file(currentFile=self.currentFile)

        self.check_protectedFile(
                handler=self.rarhandler,
                compressCurrentFile=self.currentFile,
                password=password
            )

        rarCompressorFileData = self.rarhandler.extract_content(
                                    currentFileRar=self.currentFile,
                                    password=password,
                                    resizeImage=resize
                                )

        if rarCompressorFileData == -1:
            return None
        elif rarCompressorFileData is None:
            msg = 'RAR not have images.'
            exts = self.validextentions.get_container_valid_extentions()
            msg += 'Valid Extentions:  ' + ', '.join(exts) + '\n'
            raise EmptyFile(msg)

        compressedCurrentFileIO = self.to_compressor(
                            filename=rarCompressorFileData.filename,
                            listCompressorData=[rarCompressorFileData],
                            compressor='rar',
                            join_files=False
                        )
        return compressedCurrentFileIO

    def process_dir(
        self,
        directory_path: str,
        extention_filter: Union[RAR, ZIP, PDF, CBZ, CBR, IMAGES],
        filename: str = None,
        password: str = None,
        compressor: Union[RAR, ZIP] = 'zip',
        join: bool = False,
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[List[CurrentFile], None]:
        """
        Searches files in the given directory, searches only PDF, CBZ, CBR
        files.
        By default, all files are sorted alphanumerically.

        Args:
            directory_path: directory name.
            extention_filter: 'rar', 'zip', 'pdf', 'cbz', 'cbr', 'jpeg', 'png',
                              'jpg', extension of the file to search in the
                              directory.
            filename: output file name.
            compressor: 'zip', 'rar', extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            password: password string of file, default is `None`.
            resize: string for resizing images.

        Returns:
            list: list if `CurrentFile` instance represents the data of the RAR
                  or ZIP compressor file used.
            None: if the list of images is empty, the file has no images.

        Raises:
            ValueError: if the extension used to filter the files is not valid.
            DirectoryPathNotExists: if the directory path does not exist.
            DirectoryFilterEmptyFiles: if no file matches the filter file
                                       extension.
        """
        compressor = compressor.replace('.', '').lower().strip()

        self.directory_path = directory_path

        if extention_filter == 'images':
            # handle JPG, PNG, JPEG
            return self.__images_dir(
                directory_path=directory_path,
                filename=filename,
                compressor_type=compressor,
                join=join,
                resize=resize
            )
        else:
            return self.__dir_pdf_cbr_cbz(
                directory_path=directory_path,
                extention_filter=extention_filter,
                filename=filename,
                password=password,
                compressor_type=compressor,
                join=join,
                resize=resize
            )

######################################################
#   TODO
    def __images_dir(
        self,
        directory_path: str,
        filename: str,
        compressor_type: str,
        join: str,
        resize: str
    ) -> list:
        """
        Manages the workflow of a directory containing images.

        Args
            directory_path: directory name.
            filename: output file name.
            compressor_type: 'zip', 'rar', extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            password: password string of file, default is `None`.
            resize: string for resizing images.

        Returns:
            list: list if `CurrentFile` instance represents the data of the RAR
                  or ZIP compressor file used.
            None: if the list of images is empty, the file has no images.
        """
        data = []
        self.raiser_error_compressor(compressor_str=compressor_type)

        self.__show_progress(file=directory_path)

        compressFileDataImages = self.directoryhandler.process_dir(
                        directoryPath=directory_path,
                        compressor=compressor_type,
                        resizeImage=resize,
                        join=join
                    )

        listCurrentFiles = self.to_compressor(
                                filename=directory_path,
                                listCompressorData=compressFileDataImages,
                                compressor=compressor_type,
                                join_files=join
                            )

        data += listCurrentFiles
        if data != []:
            return data
        else:
            return None

#   TODO
######################################################

    def __dir_pdf_cbr_cbz(
        self,
        directory_path: str,
        extention_filter: str,
        filename: str,
        password: str,
        compressor_type: str,
        join: str,
        resize: str
    ) -> list:
        """
        Manages the workflow for PDF, CBR, CBZ, RAR, ZIP files within a
        directory.

        Args
            directory_path: directory name.
            extention_filter: 'rar', 'zip', 'pdf', 'cbz', 'cbr' extension of
                              the file to search in the directory.
            filename: output file name.
            compressor_type: 'zip', 'rar', extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            password: password string of file, default is `None`.
            resize: string for resizing images.

        Returns
            list: list if `CurrentFile` instance represents the data of the RAR
                  or ZIP compressor file used.
            None: if the list of images is empty, the file has no images.
        """
        valids_extentions = [
                    ValidExtentions.PDF[1:],
                    ValidExtentions.CBZ[1:],
                    ValidExtentions.CBR[1:],
                    ValidExtentions.ZIP[1:],
                    ValidExtentions.RAR[1:]
                ]

        if extention_filter.lower() not in valids_extentions:
            raise ValueError('Extention not valid!.')

        self.raiser_error_compressor(compressor_str=compressor_type)

        dir_abs_path = self.paths.get_abs_path(directory_path)
        if not self.paths.exists(dir_abs_path):
            raise DirectoryPathNotExists(dir_path=directory_path)

        filesMatch = self.paths.get_file_glob(
                            extention=extention_filter,
                            directory=directory_path
                        )

        if len(filesMatch) == 0:
            raise DirectoryFilterEmptyFiles(
                            dir_path=self.directory_path,
                            filter=extention_filter
                        )
        elif len(filesMatch) > 0:
            filesMatch.sort()  # sort file names alphanumerically.
            # print(list_filePaths)
            data_Return = []
            list_ComicFiles = []  # CBR CBZ
            list_ContentCompressorFile = []  # ZIP, RAR, PDF

            for item_path in filesMatch:

                self.__show_progress(file=item_path)

                if not self.paths.exists(item_path):
                    pass
                else:
                    compressFileData = None
                    fileCurrentData = self.read(filename=item_path)

                    self.check_file(currentFile=fileCurrentData)

                    extention = fileCurrentData.extention

                    if extention == '.pdf':
                        # print('>> DIR PDF')
                        compressFileData = self.pdfphandler.process_pdf(
                                                currentFilePDF=fileCurrentData,
                                                compressor=compressor_type,
                                                resizeImage=resize
                                        )

                    elif extention == '.zip' or extention == '.cbz':
                        # print('>> DIR ZIP')
                        self.check_protectedFile(
                                    handler=self.ziphandler,
                                    compressCurrentFile=fileCurrentData,
                                    password=password
                                )
                        compressFileData = self.ziphandler.extract_content(
                                                currentFileZip=fileCurrentData,
                                                password=password,
                                                resizeImage=resize,
                                                is_join=join
                                            )

                    elif extention == '.rar' or extention == '.cbr':
                        # print('>> DIR RAR')
                        self.check_protectedFile(
                                    handler=self.rarhandler,
                                    compressCurrentFile=fileCurrentData,
                                    password=password
                                )

                        compressFileData = self.rarhandler.extract_content(
                                                currentFileRar=fileCurrentData,
                                                password=password,
                                                resizeImage=resize,
                                                is_join=join
                                            )

                        # print(compressFileData.items, type(compressFileData))
                    if compressFileData == -1:
                        pass
                    elif compressFileData is not None:
                        if compressFileData.items == 1:
                            item = compressFileData.list_data[0]
                            if item.is_comic:
                                list_ComicFiles.append(item)
                            else:
                                list_ContentCompressorFile.append(
                                                            compressFileData
                                                        )
                        else:
                            list_ContentCompressorFile.append(
                                                            compressFileData
                                                        )
#
            # print(len(list_ContentCompressorFile))
            if filename is None:
                dir_name = self.paths.get_dirname_level(
                                            path=self.directory_path,
                                            level=0
                                        )
                filenameCompressor = dir_name
            else:
                filenameCompressor = filename

            if len(list_ContentCompressorFile) > 0:
                listCurrentFiles = self.to_compressor(
                                filename=filenameCompressor,
                                listCompressorData=list_ContentCompressorFile,
                                compressor=compressor_type,
                                join_files=join
                            )
                data_Return += listCurrentFiles

            if len(list_ComicFiles) > 0:
                data_Return += list_ComicFiles

            if data_Return != []:
                return data_Return
            else:
                return None

    def to_compressor(
        self,
        listCompressorData: List[CompressorFileData],
        join_files: bool,
        filename: str = None,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> List[CurrentFile]:
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
        if type(listCompressorData) is not list:
            listCompressorData = [listCompressorData]

        # print(filename)
        if compressor == 'zip':
            compressorFile = self.ziphandler.to_zip(
                                filenameZIP=filename,
                                listZipFileCompress=listCompressorData,
                                join=join_files
                            )
        elif compressor == 'rar':
            compressorFile = self.rarhandler.to_rar(
                                filenameRAR=filename,
                                listRarFileCompress=listCompressorData,
                                join=join_files
                            )
        # print(compressorFile)
        if compressorFile is None:
            return None
        return compressorFile

    def to_write(
        self,
        listCurrentFiles: List[CurrentFile],
        path: str = '.'
    ) -> Union[List[dict], None]:
        """
        Write data from a list of `CurrentFile` instances.

        Args:
            listCurrentFiles: list of `CurrentFile` instances.
            path: location where the final file will be stored. Default is
                  `'.'`.
        Returns:
            dict: file/s information.
        """
        info_list = []
        # print(listCurrentFiles)
        if listCurrentFiles is None:
            return None

        if self.directory_path is not None:
            basenameDirectory = self.paths.get_dirname_level(
                                                path=self.directory_path,
                                                level=-1
                                            )
            if len(listCurrentFiles) == 1:
                listCurrentFiles[0].name = basenameDirectory

            base_path = self.paths.build(
                        path, ComicPy.PREFIX_CONVERTED, basenameDirectory,
                        make=True
                    )
        elif self.filename is not None:
            name_, extention_ = self.paths.splitext(self.filename)
            base_path = self.paths.build(
                        path, ComicPy.PREFIX_CONVERTED, name_,
                        make=True
                    )
        else:
            base_path = self.paths.build(
                        path, ComicPy.PREFIX_CONVERTED,
                        make=True
                    )

        for itemCurrent in listCurrentFiles:
            # print(itemCurrent.filename, itemCurrent.name)

            file_name = '%s%s' % (
                            itemCurrent.name,
                            itemCurrent.extention
                        )

            path_output = self.paths.build(base_path, file_name)

            if self.paths.exists(path_output):
                file_name = '%s_%s%s' % (
                                itemCurrent.name,
                                id(itemCurrent),
                                itemCurrent.extention
                            )
                path_output = self.paths.build(base_path, file_name)

            # Sets destine path to CurrentFile instance.
            itemCurrent.path = path_output

            if itemCurrent.extention == ValidExtentions.CBR:
                infoFileRar = self.rarhandler.to_write(
                                            currentFileRar=itemCurrent
                                        )
                info_list.append(infoFileRar)
            if itemCurrent.extention == ValidExtentions.CBZ:
                infoFileZip = self.ziphandler.to_write(
                                            currentFileZip=itemCurrent
                                        )
                info_list.append(infoFileZip)
        return info_list

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

    def __show_progress(
        self,
        file: str
    ) -> None:
        if self.show_progress:
            if self.paths.isdir(path=file):
                print('Current directory:  %s' % file)
            elif self.paths.isfile(path=file):
                print('Current file:  %s' % file)

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
