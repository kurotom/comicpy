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

PYPDF = TypeVar('pypdf')
PYMUPDF = TypeVar('pymupdf')


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
        dest: str = '.',
        compressor: Union[RAR, ZIP] = 'zip',
        resize: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve',
        motor: Union[PYPDF, PYMUPDF] = 'pypdf'
    ) -> Union[List[dict], None]:
        """
        Process PDF file, load content, extract images.

        Args:
            filename: str -> PDF file name.
            compressor:
            resize:
            motor: motor to use, `pypdf` or `pymupdf`, default `pypdf`.

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
                            resizeImage=resize,
                            motor=motor,
                            is_join=False
                        )
        if compressFileData is None:
            raise EmptyFile('File PDF not have images.')

        BASE_DIR_, CONVERTED_COMICPY_PATH_ = self.get_base_converted_path(
                                                    filename=filename,
                                                    dest_path=dest
                                                )

        list_metaFileCompress = self.to_compressor(
                                filename=filename,
                                basedir=BASE_DIR_,
                                listCompressorData=compressFileData.list_data,
                                join_files=False,
                                compressor=compressor,
                                dest=CONVERTED_COMICPY_PATH_,
                            )

        return list_metaFileCompress

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
            filename: str -> ZIP file name.
            password: password of ZIP file.
            resize: rescaling image.

        Returns:
            CurrentFile: instance representing the data of the ZIP file named
                         CBZ.
        """
        data_metadata = []

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

        BASE_DIR_, CONVERTED_COMICPY_PATH_ = self.get_base_converted_path(
                                                    filename=filename,
                                                    dest_path=dest
                                                )

        no_comic_files = []
        for item in zipCompressorFileData.list_data:
            if item.is_comic:
                metaFileCompress = self.to_write(
                                            listCurrentFiles=[item],
                                            path=CONVERTED_COMICPY_PATH_
                                        )
                data_metadata += metaFileCompress
            else:
                no_comic_files.append(item)

        if no_comic_files == []:
            return data_metadata
        else:
            list_metaFileCompress = self.to_compressor(
                                        filename=filename,
                                        basedir=BASE_DIR_,
                                        listCompressorData=no_comic_files,
                                        join_files=False,
                                        compressor='zip',
                                        dest=CONVERTED_COMICPY_PATH_,
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
            filename: str -> RAR file name.
            password: password of RAR file.
            resize: rescaling image.

        Returns:
            CurrentFile: the instance represents the data of the RAR archive
                         with the name CBR
        """
        data_metadata = []

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

        # print(rarCompressorFileData, type(rarCompressorFileData))
        BASE_DIR_, CONVERTED_COMICPY_PATH_ = self.get_base_converted_path(
                                                    filename=filename,
                                                    dest_path=dest
                                                )

        no_comic_files = []
        for item in rarCompressorFileData.list_data:
            if item.is_comic:
                metaFileCompress = self.to_write(
                                            listCurrentFiles=[item],
                                            path=CONVERTED_COMICPY_PATH_
                                        )
                data_metadata += metaFileCompress
            else:
                no_comic_files.append(item)

        if no_comic_files == []:
            return data_metadata
        else:
            list_metaFileCompress = self.to_compressor(
                                        filename=filename,
                                        basedir=BASE_DIR_,
                                        listCompressorData=no_comic_files,
                                        join_files=False,
                                        compressor='rar',
                                        dest=CONVERTED_COMICPY_PATH_,
                                    )
            data_metadata += list_metaFileCompress

        return data_metadata

    def process_dir(
        self,
        directory_path: str,
        extention_filter: Union[RAR, ZIP, PDF, CBZ, CBR, IMAGES],
        filename: str = None,
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
            filename: output file name.
            compressor: 'zip', 'rar', extension of the compressor used.
            join: boolean, if `True` all files are consolidated into one,
                  otherwise, if `False` they are kept in individual files.
            password: password string of file, default is `None`.
            resize: string for resizing images.
            motor: motor to use, `pypdf` or `pymupdf`, default `pypdf`.

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

        BASE_DIR_, CONVERTED_COMICPY_PATH_ = self.get_base_converted_path(
                                        filename=self.paths.get_dirname_level(
                                                    directory_path, level=-1),
                                        dest_path=dest
                                    )

        try:
            if extention_filter == 'images':
                # handle JPG, PNG, JPEG
                return self.__images_dir(
                    directory_path=directory_path,
                    filename=filename,
                    basedir=BASE_DIR_,
                    dest_file=CONVERTED_COMICPY_PATH_,
                    compressor_type=compressor,
                    join=join,
                    resize=resize
                )
            else:
                return self.__dir_pdf_cbr_cbz(
                    directory_path=directory_path,
                    extention_filter=extention_filter,
                    filename=filename,
                    basedir=BASE_DIR_,
                    dest_file=CONVERTED_COMICPY_PATH_,
                    password=password,
                    compressor_type=compressor,
                    join=join,
                    resize=resize,
                    motor=motor
                )
        except KeyboardInterrupt:
            print('Interrump')
            return []
        except Exception:
            return []

    def __images_dir(
        self,
        directory_path: str,
        filename: str,
        basedir: str,
        compressor_type: str,
        join: str,
        resize: str,
        dest_file: str = '.',
    ) -> Union[List[dict], None]:
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
            return None

        # print(compressFileDataImages)
        for item in compressFileDataImages:
            # print(item.filename, directory_path, filename)
            filename_ = self.paths.build(directory_path, item.filename)
            listCurrentFiles = self.to_compressor(
                                        listCompressorData=item.list_data,
                                        join_files=join,
                                        basedir=basedir,
                                        filename=filename_,
                                        dest=dest_file,
                                        compressor=compressor_type
                                    )
            if join is False:
                data_metadata += listCurrentFiles

        if join:
            return listCurrentFiles
        else:
            return data_metadata

    def __dir_pdf_cbr_cbz(
        self,
        directory_path: str,
        extention_filter: str,
        filename: str,
        basedir: str,
        password: str,
        compressor_type: str,
        join: str,
        resize: str,
        dest_file: str = '.',
        motor: Union[PYPDF, PYMUPDF] = 'pypdf'
    ) -> Union[List[dict], None]:
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
            motor: motor to use, `pypdf` or `pymupdf`, default `pypdf`.

        Returns
            list: list if `CurrentFile` instance represents the data of the RAR
                  or ZIP compressor file used.
            None: if the list of images is empty, the file has no images.
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
            raise ValueError('Extention not valid!.')

        self.raiser_error_compressor(compressor_str=compressor_type)

        dir_abs_path = self.paths.get_abs_path(directory_path)
        if not self.paths.exists(dir_abs_path):
            raise DirectoryPathNotExists(dir_path=directory_path)

        list_extention = [
                            extention_filter.lower(),
                            extention_filter.upper()
                        ]
        filesMatch = self.paths.get_files_recursive(
                            directory=directory_path,
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
                compressFileData = None
                fileCurrentData = None

                self.__show_progress(file=item_path)

                if not self.paths.exists(item_path):
                    pass
                else:
                    fileCurrentData = self.read(filename=item_path)

                    self.check_file(currentFile=fileCurrentData)

                    extention = fileCurrentData.extention

                    if extention == '.pdf':
                        # print('>> DIR PDF')
                        compressFileData = self.pdfphandler.process_pdf(
                                                currentFilePDF=fileCurrentData,
                                                compressor=compressor_type,
                                                resizeImage=resize,
                                                motor=motor,
                                                is_join=join
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
                    # print(
                    #     compressFileData.items,
                    #     len(data_metadata)
                    # )
                    if compressFileData == -1:
                        pass
                    elif compressFileData is not None:
                        comicsItem = [
                                    i for i in compressFileData.list_data
                                    if i.is_comic
                                ]

                        if len(comicsItem) > 0:
                            for itemComic in comicsItem:
                                metaFileCompress = self.to_write(
                                            listCurrentFiles=[itemComic],
                                            path=dest_file
                                        )
                                data_metadata += metaFileCompress
                        else:
                            item = compressFileData
                            filename_ = self.paths.build(
                                                directory_path,
                                                item.filename
                                            )
                            metadataFiles = self.to_compressor(
                                            filename=filename_,
                                            basedir=basedir,
                                            listCompressorData=item.list_data,
                                            dest=dest_file,
                                            join_files=join,
                                            compressor=compressor_type
                                        )
                            data_metadata += metadataFiles
                        comicsItem = None

            self.__reset_names_counter_handlers()

            return data_metadata

    def file_merger_handler(
        self,
        list_compressorFile: List[CompressorFileData],
        compressor: str,
        is_join: bool
    ) -> List[CompressorFileData]:
        """
        Restructures the data of RAW files depending on whether they should be
        merged or not.

        Args
            list_compressorFile: list of `CompressorFileData` instances.
            compressor: type of compressor to use.
            is_join: boolean if the files will be joined.

         Returns
            List[CompressorFileData]: list of `CompressorFileData` instances.
        """
        files_ = {}
        main_dir_ = False
        name_file_join_ = None
        results = []

        for itemCompress in list_compressorFile:
            if is_join is False:
                results.append(itemCompress)
            else:
                for item in itemCompress.list_data:
                    name_dir_ = self.paths.get_dirname_level(
                                            path=item.filename,
                                            level=-1
                                        )
                    if name_dir_ == '.':
                        name_, extention_ = self.paths.splitext(
                                        self.paths.get_basename(item.filename)
                                    )
                        name_dir_ = name_

                    if main_dir_ is False:
                        if name_dir_ not in files_:
                            files_[name_dir_] = [item]
                            main_dir_ = True
                            name_file_join_ = name_dir_
                    else:
                        files_[name_file_join_].append(item)

        # print(name_file_join_, files_.keys(), len(list(files_.values())[0]))
        if is_join:
            compressorJoinFiles = CompressorFileData(
                                    filename=name_file_join_,
                                    list_data=list(files_.values())[0],
                                    type=compressor,
                                    unit=self.unit
                                )
            results.append(compressorJoinFiles)
        return results

    def __reset_names_counter_handlers(self) -> None:
        """
        Resets CBR or CBZ names and counters of images in handlers.
        """
        self.ziphandler.reset_names()
        self.rarhandler.reset_names()
        self.pdfphandler.reset_counter()
        self.directoryhandler.reset_counter()

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
            dataRawFile: list of CompressorFileData instances, this class
                         contains image list data, filename, etc.
            filename: name of the output file.
            dest: destine to final file.
            compressor: ['rar', 'zip'], by default `zip`, compressor to use.

        Returns:
            list: list of directories of metadata of file CBR o CBZ.
            None: if the list of images is empty, the file has no images.
        """
        if type(listCompressorData) is not list:
            listCompressorData = [listCompressorData]

        # print(filename)
        if compressor == 'zip':
            metadata = self.ziphandler.to_zip(
                                filenameZIP=filename,
                                basedir=basedir,
                                data_list=listCompressorData,
                                join=join_files,
                                converted_comicpy_path=dest,
                            )
        elif compressor == 'rar':
            metadata = self.rarhandler.to_rar(
                                filenameRAR=filename,
                                basedir=basedir,
                                data_list=listCompressorData,
                                join=join_files,
                                converted_comicpy_path=dest,
                            )
        # print('--> ', type(metadata))
        if metadata is None:
            return None
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
            dict: file/s information.
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
        filename: str,
        dest_path: str
    ) -> tuple:
        """
        Gets name of file and path to save file CBR or CBZ.

        Args
            filename: file.
            dest_path: location to save file given for user.

        Returns
            tuple: filename without extention and path to save CBR or CBZ file.
        """
        filename = filename.replace(' ', '_')
        dest_path = dest_path.replace(' ', '_')
        BASE_DIR_, extention_ = self.paths.splitext(
                                        self.paths.get_basename(filename)
                                    )
        CONVERTED_COMICPY_PATH_ = self.paths.build(
                                            dest_path,
                                            ComicPy.PREFIX_CONVERTED,
                                            BASE_DIR_,
                                            make=True
                                        )
        return BASE_DIR_, CONVERTED_COMICPY_PATH_

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
