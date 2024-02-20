# -*- coding: utf-8 -*-
"""
"""

from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData
)
from comicpy.valid_extentions import imagesExtentions

from uuid import uuid1
import subprocess
import shutil
import rarfile
import io
import os

from typing import List, Union


class RarHandler:

    def rename_rar_cbr(
        self,
        currentFileRar: CurrentFile
    ) -> CurrentFile:
        currentFileRar.extention = '.cbr'
        currentFileRar.name = currentFileRar.name.replace(' ', '_')
        return currentFileRar

    def extract_images(
        self,
        currentFileRar: CurrentFile
    ) -> List[ImageComicData]:
        rawDataRar = currentFileRar.bytes_data
        listImageComicData = []
        with rarfile.RarFile(
            file=rawDataRar,
            mode='r'
        ) as rar_file:

            directory_name = None

            for item in rar_file.namelist():

                directory_name = os.path.dirname(item).replace(' ', '_')
                name_file = os.path.basename(item)
                _name, _extention = os.path.splitext(name_file)

                if _extention in list(imagesExtentions.values()):
                    # print(_name, _extention, directory_name)
                    item_name = name_file.replace(' ', '_')
                    file_name = os.path.join(directory_name, item_name)

                    dataImage = rar_file.read(item)
                    image_comic = ImageComicData(
                                    filename=file_name,
                                    bytes_data=io.BytesIO(dataImage)
                                )
                    listImageComicData.append(image_comic)

        rarFileCompress = CompressorFileData(
                                    filename=directory_name,
                                    list_data=listImageComicData,
                                    type='rar',
                                )
        return rarFileCompress

    def to_rar(
        self,
        filenameRAR: str,
        listRarFileCompress: List[CompressorFileData]
    ) -> Union[CurrentFile, None]:
        # print(listRarFileCompress)
        buffer_dataRar = io.BytesIO()

        id_directory = uuid1().hex
        ROOT_DIRECTORY = '.RAR_TEMP'
        ROOT_PATH = os.path.join(ROOT_DIRECTORY, id_directory)

        DIR_RAR_FILES = os.path.join(ROOT_PATH, filenameRAR)
        RAR_FILE_ = os.path.join(DIR_RAR_FILES) + '.rar'
        # print(ROOT_PATH)

        # Make directory and save all data into `.RAR_TEMP`
        if not os.path.exists(DIR_RAR_FILES):
            os.makedirs(DIR_RAR_FILES)

        for item in listRarFileCompress:
            # print(item, len(item.list_data), item.filename)
            directory_path = os.path.join(DIR_RAR_FILES, item.filename)

            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            for image in item.list_data:
                file_name = os.path.basename(image.filename)
                image_path = os.path.join(directory_path, file_name)
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

            # print(buffer_dataRar.getbuffer().nbytes)
            # print(type(obj), buffer_dataRar.getbuffer().nbytes)

            # Clear Temp Directory and RAR File.
            shutil.rmtree(path=ROOT_PATH)

            rarFileCurrent = CurrentFile(
                                filename='FileRar',
                                bytes_data=buffer_dataRar,
                            )
            return rarFileCurrent

        else:
            return None

    def to_write(
        self,
        currentFileRar: CurrentFile
    ) -> dict:
        fileRar = currentFileRar.name + currentFileRar.extention
        with open(fileRar, 'wb') as file:
            file.write(currentFileRar.bytes_data.getvalue())

        return {
            'name': fileRar,
            'size': currentFileRar.size
        }
