# -*- coding: utf-8 -*-
"""
Handler related to files ZIP.
"""

from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData
)

from comicpy.handlers.baseziprar import BaseZipRarHandler

from comicpy.valid_extentions import imagesExtentions

import zipfile
import io
import os

from typing import List, Union


class ZipHandler(BaseZipRarHandler):
    """
    Class in charge of extract images, rename file ZIP, create ZIP file, write
    data into ZIP file.
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

    def rename_zip_cbz(
        self,
        currentFileZip: CurrentFile
    ) -> CompressorFileData:
        """
        Add CBZ name and extention of `CurrentFile` instance.

        Args:
            CurrentFile: instance with data ZIP file.

        Returns:
            CurrentFile: same instance with new name and extention.
        """
        currentFileZip.extention = '.cbz'
        currentFileZip.name = currentFileZip.name.replace(' ', '_')
        zipFileCompress = CompressorFileData(
                                    filename=currentFileZip.name,
                                    list_data=[currentFileZip],
                                    type='zip',
                                    unit=self.unit,
                                    join=False,
                                )
        return zipFileCompress

    def extract_images(
        self,
        currentFileZip: CurrentFile,
        password: str = None
    ) -> CompressorFileData:
        """
        Extract images from ZIP file.

        Args:
            currentFile: `CurrentFile` instance with data of original ZIP file.
            password: password string of file, default is `None`.

        Returns:
            CompressorFileData: instances contains name of directory of images,
                                list of ImageComicData instances, type of
                                compressor.
        """
        listImageComicData = []
        directory_name = None
        dataBytesIO = currentFileZip.bytes_data

        with zipfile.ZipFile(
            file=dataBytesIO,
            mode='r'
        ) as zip_file:

            for item in zip_file.namelist():

                directory_name = os.path.dirname(item).replace(' ', '_')
                name_file = os.path.basename(item)
                _name, _extention = os.path.splitext(name_file)

                if _extention in list(imagesExtentions.values()):
                    # print(_name, _extention, directory_name)
                    item_name = name_file.replace(' ', '_')
                    file_name = os.path.join(directory_name, item_name)

                    dataImage = zip_file.read(
                                        item,
                                        pwd=password
                                    )

                    image_comic = ImageComicData(
                                    filename=file_name,
                                    bytes_data=io.BytesIO(dataImage),
                                    unit=self.unit
                                )
                    listImageComicData.append(image_comic)

        zipFileCompress = CompressorFileData(
                                    filename=directory_name,
                                    list_data=listImageComicData,
                                    type='zip',
                                    unit=self.unit
                                )
        return zipFileCompress

    def to_zip(
        self,
        listZipFileCompress: List[CompressorFileData],
        join: bool,
        filenameZIP: str = None,
    ) -> Union[List[CurrentFile], None]:
        """
        Handles how the data in the ZIP file(s) should be written.

        Args:
            listZipFileCompress: list of CompressorFileData instances.
            filenameZIP: name of the ZIP archive.

        Returns:
            CurrentFile: the instance contains bytes of the ZIP file.
            List[CurrentFile]: list of instances contains bytes of the ZIP
                               file.
            None: if `subprocess.run` fails.
        """
        if len(listZipFileCompress) == 0:
            return None

        data_of_zips = []
        if join is True:
            currentFileZip = self.__to_zip_data(
                    listZipFileCompress=listZipFileCompress,
                    filenameZIP=filenameZIP
                )
            data_of_zips.append(currentFileZip)
        elif join is False:
            for file in listZipFileCompress:
                current_file_list = [file]
                currentFileZip = self.__to_zip_data(
                        listZipFileCompress=current_file_list,
                        filenameZIP=file.filename
                    )
                data_of_zips.append(currentFileZip)

        zipCompressorData = CompressorFileData(
                filename=filenameZIP,
                list_data=data_of_zips,
                type='zip',
                join=join
            )
        return zipCompressorData

    def __to_zip_data(
        self,
        listZipFileCompress: List[CompressorFileData],
        filenameZIP: str = None,
    ) -> CurrentFile:
        """
        Write data of `CompressorFileData` into ZIP file.

        Args:
            listZipFileCompress: list of `CompressorFileData` instances with
                                 ZIP compressor data.
            filenameZIP: name of file ZIP.

        Returns:
            CurrentFile: with data of ZIP file.
        """

        if filenameZIP is None:
            filenameZIP = 'FileZip'

        buffer_dataZip = io.BytesIO()
        with zipfile.ZipFile(
            file=buffer_dataZip, mode='a',
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=False
        ) as zip_file:
            for item in listZipFileCompress:
                # print(item, len(item.list_data), item.filename)

                directory_path = item.filename

                info_archivo_zip = zipfile.ZipInfo(filename=directory_path)
                info_archivo_zip.compress_type = zipfile.ZIP_DEFLATED

                for image in item.list_data:
                    image_path = os.path.join(directory_path, image.filename)
                    zip_file.writestr(
                            zinfo_or_arcname=image_path,
                            data=image.bytes_data.getvalue()
                        )

        zipFileCurrent = CurrentFile(
                            filename=filenameZIP,
                            bytes_data=buffer_dataZip,
                            unit=self.unit,
                            extention='.cbz'
                        )
        return zipFileCurrent

    def to_write(
        self,
        currentFileZip: CompressorFileData,
        path_dest: str
    ) -> List[dict]:
        """
        Send data to `BaseZipRarHandler.to_write()` to save the ZIP file data.

        Args:
            currentFileRar: `CompressorFileData` instance, contains data of
                            ZIP file.
            path_dest: location where the CBZ file will be stored.

        Returns:
            List[dict]: list of dicts with information of all files saved.
                        'name': path to the file.
                        'size': size of file.
        """
        return super().to_write(
                            currentCompressorFile=currentFileZip,
                            path=path_dest
                        )
