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
    DirectoryEmptyFilesValid,
    UnitFileSizeInvalid,
    FilePasswordProtected,
    InvalidCompressor,
    ExtentionError
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

PYPDF = TypeVar('pypdf')
PYMUPDF = TypeVar('pymupdf')


class ComicPy:
    """
    Class in charge of manipulating the workflow, loading data from file(s),
    verifying, extracting images, saving to final `CBZ` or `CBR` file.
    """
    PATH_CONVERTED_ = 'Converted_comicpy'

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
        self.checker = CheckFile()
        self.directoryhandler = DirectoryHandler(unit=self.unit)
        self.ziphandler = ZipHandler(unit=self.unit)
        self.pdfphandler = PdfHandler(unit=self.unit)
        self.rarhandler = RarHandler(unit=self.unit)
        self.paths = Paths()
        self.validextentions = ValidExtentions()

        self.join_files = False
        self.BASE_DIR_ = None
        self.CONVERTED_COMICPY_PATH_ = None
        self.FILE_CBR_CBZ_ = None
        self.LAST_ITEM_ = False

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
            raise InvalidCompressor

    def load_file(
        self,
        filename: str
    ) -> bytes:
        """
        Load file given, sets attributes `filename`, `currentFile`.
        """
        self.filename = filename
        return self.read(filename=self.filename)

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
        dest: str = '.',
        compressor: Union[RAR, ZIP] = 'zip',
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve',
        motor: Union[PYPDF, PYMUPDF] = 'pypdf'
    ) -> Union[List[dict], None]:
        """
        Process PDF file, load content, extract images.

        Args:
            filename: PDF file name.
            dest: destination path of CBZ or CBR files, default is '.'.
            compressor: type of compressor, 'rar' or 'zip', default is 'zip'.
            resize: resize images, default is 'preserve'
            motor: motor to use, `pypdf` or `pymupdf`, default `pypdf`.

        Returns:
            list: list of diccionaries with metadata of file/s CBZ or CBR.
        """
        metaFileCompress = []

        self.__show_progress(file=filename)

        file_raw = self.load_file(filename=filename)

        compressor = compressor.replace('.', '').lower().strip()

        self.raiser_error_compressor(compressor_str=compressor)

        self.check_file(currentFile=file_raw)

        compressFileData = self.pdfphandler.process_pdf(
                            currentFilePDF=file_raw,
                            compressor=compressor,
                            resizeImage=resize,
                            motor=motor,
                            is_join=self.join_files
                        )
        if compressFileData is None:
            raise EmptyFile('File PDF not have images.')

        if self.directory_path is None:
            self.get_base_converted_path(
                    origin=filename,
                    dest=dest,
                    type='f'
                )

        self.get_cbz_cbr_name(
                filename=filename,
                compressor=compressor
            )

        metaFileCompress = self.to_compressor(
                                filename=self.FILE_CBR_CBZ_,
                                basedir=self.BASE_DIR_,
                                listCompressorData=compressFileData.list_data,
                                join_files=self.join_files,
                                compressor=compressor,
                                dest=self.CONVERTED_COMICPY_PATH_,
                            )

        return metaFileCompress

    def process_zip(
        self,
        filename: str,
        dest: str = '.',
        password: str = None,
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[List[dict], None]:
        """
        Process ZIP files.

        Args:
            filename: ZIP file name.
            dest: destination path of CBZ files, default is '.'.
            password: password of ZIP file.
            resize: rescaling image.

        Returns:
            list: list of diccionaries with metadata of file/s CBZ.
        """
        data_metadata = []

        self.__show_progress(file=filename)

        file_raw = self.load_file(filename=filename)

        self.check_file(currentFile=file_raw)

        self.check_protectedFile(
                handler=self.ziphandler,
                compressCurrentFile=file_raw,
                password=password
            )
        zipCompressorFileData = self.ziphandler.extract_content(
                                    currentFileZip=file_raw,
                                    password=password,
                                    resizeImage=resize,
                                    is_join=self.join_files
                                )

        if zipCompressorFileData is None or zipCompressorFileData == -1:
            msg = '\nZIP file not have files with '
            exts = self.validextentions.get_container_valid_extentions()
            msg += 'valid Extentions: ' + ', '.join(exts) + '\n'
            raise EmptyFile(msg)

        if self.directory_path is None:
            self.get_base_converted_path(
                    origin=filename,
                    dest=dest,
                    type='f'
                )

        self.get_cbz_cbr_name(
                filename=filename,
                compressor='zip'
            )

        no_comic_files = []
        for item in zipCompressorFileData.list_data:
            if item.is_comic:
                metaFileCompress = self.to_write(
                                            listCurrentFiles=[item],
                                            path=self.CONVERTED_COMICPY_PATH_
                                        )
                data_metadata += metaFileCompress
            else:
                no_comic_files.append(item)

        if no_comic_files == []:
            return data_metadata
        else:
            list_metaFileCompress = self.to_compressor(
                                        filename=self.FILE_CBR_CBZ_,
                                        basedir=self.BASE_DIR_,
                                        listCompressorData=no_comic_files,
                                        join_files=self.join_files,
                                        compressor='zip',
                                        dest=self.CONVERTED_COMICPY_PATH_
                                    )
            data_metadata += list_metaFileCompress

        return data_metadata

    def process_rar(
        self,
        filename: str,
        dest: str = '.',
        password: str = None,
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[List[dict], None]:
        """
        Process RAR files.

        Args:
            filename: RAR file name.
            dest: destination path of CBR files, default is '.'.
            password: password of RAR file.
            resize: rescaling image.

        Returns:
            list: list of diccionaries with metadata of file/s CBR.
        """
        data_metadata = []

        self.__show_progress(file=filename)

        file_raw = self.load_file(filename=filename)

        self.check_file(currentFile=file_raw)

        self.check_protectedFile(
                handler=self.rarhandler,
                compressCurrentFile=file_raw,
                password=password
            )

        rarCompressorFileData = self.rarhandler.extract_content(
                                    currentFileRar=file_raw,
                                    password=password,
                                    resizeImage=resize,
                                    is_join=self.join_files
                                )

        if rarCompressorFileData is None or rarCompressorFileData == -1:
            msg = '\nRAR file not have files with '
            exts = self.validextentions.get_container_valid_extentions()
            msg += 'valid Extentions: ' + ', '.join(exts) + '\n'
            raise EmptyFile(msg)

        if self.directory_path is None:
            self.get_base_converted_path(
                    origin=filename,
                    dest=dest,
                    type='f'
                )

        self.get_cbz_cbr_name(
                filename=filename,
                compressor='rar'
            )

        no_comic_files = []
        for item in rarCompressorFileData.list_data:
            if item.is_comic:
                metaFileCompress = self.to_write(
                                            listCurrentFiles=[item],
                                            path=self.CONVERTED_COMICPY_PATH_
                                        )
                data_metadata += metaFileCompress
            else:
                no_comic_files.append(item)

        if no_comic_files == []:
            return data_metadata
        else:
            list_metaFileCompress = self.to_compressor(
                                        filename=self.FILE_CBR_CBZ_,
                                        basedir=self.BASE_DIR_,
                                        listCompressorData=no_comic_files,
                                        join_files=self.join_files,
                                        compressor='rar',
                                        dest=self.CONVERTED_COMICPY_PATH_
                                    )
            data_metadata += list_metaFileCompress

        return data_metadata

    def process_dir(
        self,
        directory_path: str,
        extention_filter: Union[RAR, ZIP, PDF, CBZ, CBR, IMAGES],
        dest: str = '.',
        password: str = None,
        compressor: Union[RAR, ZIP] = 'zip',
        join: bool = False,
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve',
        motor: Union[PYPDF, PYMUPDF] = 'pypdf'
    ) -> Union[List[dict], None]:
        """
        Searches files in the given directory, searches only PDF, CBZ, CBR
        files.
        By default, all files are sorted alphanumerically.

        Args:
            directory_path: directory name.
            extention_filter: 'rar', 'zip', 'pdf', 'cbz', 'cbr', 'jpeg', 'png',
                              'jpg', extension of the file to search in the
                              directory.
            dest: destination path of CBZ or CBR files, default is '.'.
            password: password string of file, default is `None`.
            compressor: 'zip', 'rar', extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            resize: string for resizing images, default is 'preserve'.
            motor: motor to use, `pypdf` or `pymupdf`, default `pypdf`.

        Returns:
            list: list of diccionaries with metadata of file/s CBR or CBZ.
            None: if the list of images is empty, the file has no images.
        """
        compressor = compressor.replace('.', '').lower().strip()

        self.directory_path = self.paths.get_abs_path(path=directory_path)
        self.join_files = join

        self.get_base_converted_path(
                origin=directory_path,
                dest=dest,
                type='d'
            )

        # print(self.BASE_DIR_, self.CONVERTED_COMICPY_PATH_)

        try:
            if extention_filter == 'images':
                # handle JPG, PNG, JPEG
                return self.__images_dir(
                    directory_path=directory_path,
                    compressor_type=compressor,
                    resize=resize,
                    join=join,
                    dest=dest,
                )
            else:
                return self.__dir_pdf_rar_zip(
                    directory_path=directory_path,
                    extention_filter=extention_filter,
                    password=password,
                    compressor_type=compressor,
                    join=join,
                    resize=resize,
                    motor=motor,
                    dest=dest
                )
        except KeyboardInterrupt:
            print('Interrump')
            return []
        except (
            DirectoryPathNotExists,
            DirectoryFilterEmptyFiles,
            DirectoryEmptyFilesValid,
            InvalidCompressor,
            ExtentionError,
            EmptyFile
        ) as e:
            print('%s\n' % (e))
            return []

    def __images_dir(
        self,
        directory_path: str,
        compressor_type: str,
        join: str,
        resize: str,
        dest: str = '.',
    ) -> Union[List[dict], None]:
        """
        Manages the workflow of a directory containing images.

        Args
            directory_path: directory name.
            compressor_type: 'zip', 'rar', extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            password: password string of file, default is `None`.
            resize: string for resizing images.
            dest: destination path of CBZ or CBR files, default is '.'.

        Returns:
            list: list of diccionaries with metadata of file/s CBR or CBZ.
            None: if the list of images is empty, the file has no images.

        Raises
            DirectoryEmptyFilesValid: if directory not have valid files.
        """
        data_metadata = []

        self.raiser_error_compressor(compressor_str=compressor_type)

        self.__show_progress(file=directory_path)

        compressFileDataImages = self.directoryhandler.process_dir(
                        directoryPath=directory_path,
                        compressor=compressor_type,
                        resizeImage=resize,
                        join=join
                    )

        if compressFileDataImages is None:
            raise DirectoryEmptyFilesValid(dir_path=directory_path)

        for item in compressFileDataImages:
            # print('->', item.filename, directory_path)
            if item.filename == compressFileDataImages[-1].filename:
                self.LAST_ITEM_ = True

            self.get_cbz_cbr_name(
                    filename=item.filename,
                    compressor=compressor_type
                )

            metadataFile = self.to_compressor(
                                        filename=self.FILE_CBR_CBZ_,
                                        basedir=self.BASE_DIR_,
                                        listCompressorData=item.list_data,
                                        join_files=self.join_files,
                                        compressor=compressor_type,
                                        dest=self.CONVERTED_COMICPY_PATH_
                                    )
            # print(metadataFile)

            if join is False:
                data_metadata += metadataFile

        if join:
            return metadataFile
        else:
            return data_metadata

        return []

    def __dir_pdf_rar_zip(
        self,
        directory_path: str,
        extention_filter: str,
        password: str,
        compressor_type: str,
        join: str,
        resize: str,
        dest: str = '.',
        motor: Union[PYPDF, PYMUPDF] = 'pypdf'
    ) -> Union[List[dict], None]:
        """
        Manages the workflow for PDF, CBR, CBZ, RAR, ZIP files within a
        directory.

        Args
            directory_path: directory name.
            extention_filter: 'rar', 'zip', 'pdf', 'cbz', 'cbr' extension of
                              the file to search in the directory.
            password: password string of file, default is `None`.
            compressor_type: 'zip', 'rar', extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            resize: string for resizing images, default is 'preserve'.
            dest: destination path of CBZ or CBR files, default is '.'.
            motor: motor to use, `pypdf` or `pymupdf`, default `pypdf`.

        Returns
            list: list of diccionaries with metadata of file/s CBR or CBZ.
            None: if the list of images is empty, the file has no images.

        Raises
            ExtentionError: if filter extention is not valid.
            DirectoryPathNotExists: if directory path not exists.
            DirectoryFilterEmptyFiles: if directory not have valid files.
        """
        data_metadata = []
        valids_extentions = [
                    ValidExtentions.PDF[1:],
                    ValidExtentions.CBZ[1:],
                    ValidExtentions.CBR[1:],
                    ValidExtentions.ZIP[1:],
                    ValidExtentions.RAR[1:]
                ]

        if extention_filter.lower() not in valids_extentions:
            raise ExtentionError(message=', '.join(valids_extentions))

        self.raiser_error_compressor(compressor_str=compressor_type)

        if not self.paths.exists(self.directory_path):
            raise DirectoryPathNotExists(dir_path=directory_path)

        list_extention = [
                            extention_filter.lower(),
                            extention_filter.upper()
                        ]
        filesMatch = self.paths.get_files_recursive(
                            directory=self.directory_path,
                            extentions=list_extention,
                        )

        if len(filesMatch) == 0:
            raise DirectoryFilterEmptyFiles(
                            dir_path=self.directory_path,
                            filter=extention_filter
                        )

        elif len(filesMatch) > 0:
            filesMatch.sort()  # sort file names alphanumerically.

            for item_path in filesMatch:
                # compressFileData = None
                # fileCurrentData = None

                if not self.paths.exists(item_path):
                    pass
                else:
                    if item_path == filesMatch[-1]:
                        self.LAST_ITEM_ = True

                    name_, extention_ = self.paths.splitext(
                                                path=str(item_path)
                                            )
                    extention = extention_.lower()

                    if extention == '.pdf':
                        # print('>> DIR PDF')
                        metadataFiles = self.process_pdf(
                                                filename=str(item_path),
                                                compressor=compressor_type,
                                                resize=resize,
                                                motor=motor,
                                            )
                    elif extention == '.zip' or extention == '.cbz':
                        # print('>> DIR ZIP')
                        metadataFiles = self.process_zip(
                                            filename=str(item_path),
                                            password=password,
                                            resize=resize
                                        )
                    elif extention == '.rar' or extention == '.cbr':
                        # print('>> DIR RAR')
                        metadataFiles = self.process_rar(
                                                filename=str(item_path),
                                                password=password,
                                                resize=resize
                                            )

                    if metadataFiles is not None:
                        if self.join_files:
                            if data_metadata == []:
                                data_metadata += metadataFiles
                            else:
                                data_metadata = metadataFiles
                        else:
                            data_metadata += metadataFiles

            self.__reset_names_counter_handlers()

            return data_metadata

    def __reset_names_counter_handlers(self) -> None:
        """
        Resets CBR or CBZ names and counters of images in handlers and status
        of `ComicPy`.
        """
        # handlers
        self.ziphandler.reset_names()
        self.rarhandler.reset_names()
        self.pdfphandler.reset_counter()
        self.directoryhandler.reset_counter()
        # ComicPy instance
        self.BASE_DIR_ = None
        self.CONVERTED_COMICPY_PATH_ = None
        self.join_files = False
        self.FILE_CBR_CBZ_ = None
        self.LAST_ITEM_ = False
        self.filename = None

    def to_compressor(
        self,
        listCompressorData: List[CompressorFileData],
        join_files: bool,
        filename: str = None,
        basedir: str = None,
        dest: str = None,
        compressor: Union[RAR, ZIP] = 'zip',
    ) -> List[dict]:
        """
        Convert data of list of CompressorFileData to only RAR or ZIP file.

        Args:
            listCompressorData: list of CompressorFileData instances, this
            class contains image list data, filename, etc.
            join_files: if `True` join the data, otherwise, no.
            filename: name of the output file.
            basedir: name of directory base to store files CBR or CBZ.
            dest: destine to final file.
            compressor: ['rar', 'zip'], by default `zip`, compressor to use.

        Returns:
            list: list of directories of metadata of file CBR o CBZ.
            None: if the list of images is empty, the file has no images.
        """
        if type(listCompressorData) is not list:
            listCompressorData = [listCompressorData]

        if compressor == 'zip':
            metadata = self.ziphandler.to_zip(
                                pathCBZconverted=filename,
                                basedir=basedir,
                                data_list=listCompressorData,
                                join=join_files,
                                converted_comicpy_path=dest,
                                last_item=self.LAST_ITEM_
                            )
        elif compressor == 'rar':
            metadata = self.rarhandler.to_rar(
                                pathCBRconverted=filename,
                                basedir=basedir,
                                data_list=listCompressorData,
                                join=join_files,
                                converted_comicpy_path=dest,
                                last_item=self.LAST_ITEM_
                            )

        if metadata is None:
            return None

        if metadata != []:
            metadata[0]['name'] = self.FILE_CBR_CBZ_

        return metadata

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
            dict: metadata file/s information.
        """
        info_list = []
        # print(listCurrentFiles)
        if listCurrentFiles is None:
            return None

        base_path = path

        for itemCurrent in listCurrentFiles:
            # print(itemCurrent.filename, itemCurrent.name)

            filename_ = self.paths.get_basename(path=itemCurrent.filename)

            file_name = '%s%s' % (
                            filename_,
                            itemCurrent.extention
                        )

            path_output = self.paths.build(
                                base_path,
                                file_name,
                                # make=True
                            )

            if self.paths.exists(path_output):
                file_name = '%s_%s%s' % (
                                itemCurrent.name,
                                id(itemCurrent),
                                itemCurrent.extention
                            )
                path_output = self.paths.build(base_path, file_name)

            # print(path_output)

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

        Returns
            bool: boolean if file is stored on right place and can be readed.
        """
        fileCompressed = self.read(filename=filename)
        is_valid = self.checker.check(currenf_file=fileCompressed)
        name_ = self.paths.get_basename(fileCompressed.filename)
        if show:
            string = 'File "%s" is valid?:  "%s"' % (name_, is_valid)
            print(string)
        return is_valid

    def get_base_converted_path(
        self,
        origin: str,
        dest: str,
        type: str,
    ) -> tuple:
        """
        Gets name of file and path to save file CBR or CBZ.

        Args
            origin: path of original file.
            dest: location to save file given for user.
            type: directory ("d") or file ("f").

        Returns
            tuple: filename without extention and path to save CBR or CBZ file.
        """
        if type == 'd':
            BASE_DIR_ = self.paths.get_dirname_level(
                                    path=origin,
                                    level=-1
                                )
            if BASE_DIR_ == '.':
                BASE_DIR_ = origin
            else:
                BASE_DIR_ = BASE_DIR_

        elif type == 'f':
            BASE_DIR_, extention_ = self.paths.splitext(
                                        self.paths.get_basename(origin)
                                    )

        CONVERTED_COMICPY_PATH_ = self.paths.build(
                                            dest,
                                            ComicPy.PATH_CONVERTED_,
                                            BASE_DIR_.replace(' ', '_'),
                                            make=True
                                        )

        self.BASE_DIR_ = BASE_DIR_
        self.CONVERTED_COMICPY_PATH_ = CONVERTED_COMICPY_PATH_
        return BASE_DIR_, CONVERTED_COMICPY_PATH_

    def get_cbz_cbr_name(
        self,
        filename: str,
        compressor: str
    ) -> str:
        """
        Gets name of CBR or CBZ files from originals names of files RAR or ZIP.

        Args
            filename: name of file RAR or ZIP.
            compressor: type of compressor.

        Returns:
            str: name of file CBR or CBZ.
        """
        compressor_ext = {'zip': 'cbz', 'rar': 'cbr'}
        name_, ext_ = self.paths.splitext(
                    self.paths.get_basename(filename).replace(' ', '_')
                )
        if self.join_files:
            if self.FILE_CBR_CBZ_ is None:
                path_name_cbr_cbz = self.paths.build(
                            self.CONVERTED_COMICPY_PATH_,
                            '%s.%s' % (
                                name_,
                                compressor_ext[compressor]
                            )
                        )
                self.FILE_CBR_CBZ_ = path_name_cbr_cbz
        else:
            path_name_cbr_cbz = self.paths.build(
                            self.CONVERTED_COMICPY_PATH_,
                            '%s.%s' % (
                                name_,
                                compressor_ext[compressor]
                            )
                        )
            self.FILE_CBR_CBZ_ = path_name_cbr_cbz

        return self.FILE_CBR_CBZ_

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
