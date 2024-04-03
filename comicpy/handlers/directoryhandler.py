# -*- coding: utf-8 -*-
"""
Contains class to handle images within directories, it searches images
recursively within directories, sorted alphanumerically.
"""

from comicpy.handlers.imageshandler import ImagesHandler
from comicpy.valid_extentions import ValidExtentions
from comicpy.utils import Paths

from comicpy.models import (
    CompressorFileData
)

from typing import (
    TypeVar,
    Union
)


PRESERVE = TypeVar('preserve')
SMALL = TypeVar('small')
MEDIUM = TypeVar('medium')
LARGE = TypeVar('large')
ImageInstancePIL = TypeVar("ImageInstancePIL")


class DirectoryHandler:
    """
    Class in charge of handle workflow of images in directories.
    Respecting the alphanumeric order of the images.
    Rescaling the images if indicated.
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
        self.imageshandler = ImagesHandler()
        self.paths = Paths()
        self.number_image = 1
        self.separator = self.paths.get_separator()

    def reset_counter(self) -> None:
        """
        Resets index of images.
        """
        self.number_image = 1

    def read(
        self,
        filename: str
    ) -> bytes:
        """
        Read data of image.

        Args
            filename: path of image.

        Returns
            bytes: raw data of image.
        """
        with open(filename, 'rb') as file:
            return file.read()

    def process_dir(
        self,
        directoryPath: str,
        compressor: str,
        join: bool,
        resizeImage: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[CompressorFileData, None]:
        """
        Takes a directory path, search for images and return of
        `CompressorFileData` with data of images.

        Args:
            directoryPath: directory path.
            compressor: type of compressor to use.
            join: bool if the directories are merged into one.
            resizeImage: new size of the images.

        Returns:
            CompressorFileData`: instance with all images in directories.
        """

        imagesExtentions = [
            ValidExtentions.JPEG,
            ValidExtentions.PNG,
            ValidExtentions.JPG
        ]

        basenameDirectory = self.paths.get_dirname_level(
                                            path=directoryPath,
                                            level=-1
                                        )

        filesMatches = self.paths.get_files_recursive(
                directory=directoryPath,
                extentions=imagesExtentions,
            )
        filesMatches.sort()

        filesDict = self.files_by_level(listFiles=filesMatches)

        # print(filesDict, basenameDirectory)

        listImagesData = []
        listCompressorFileData = []
        name_directory = None
        for key, listImagePath in filesDict.items():
            # print(listImagePath)
            if join is False:
                self.reset_counter()
                name_directory = key.replace(' ', '_')
            else:
                name_directory = basenameDirectory.replace(' ', '_')

            images_directory = []
            for image in listImagePath:
                file_name = image.name
                path_image = str(image)
                dataImage = self.read(filename=path_image)
                # print(basenameDirectory, path_image)

                name_, extention_ = self.paths.splitext(path=file_name)

                name_image = 'Image%s%s' % (
                                    str(self.number_image).zfill(4),
                                    extention_.lower()
                                )

                image_comic = self.imageshandler.new_image(
                                        name_image=name_image,
                                        currentImage=dataImage,
                                        extention=extention_[1:].upper(),
                                        sizeImage=resizeImage,
                                        unit=self.unit
                                    )
                image_comic.original_name = file_name

                images_directory.append(image_comic)

                self.number_image += 1

            if join is False:
                imagesDirectoryCompress = CompressorFileData(
                                        filename=name_directory,
                                        list_data=images_directory,
                                        type=compressor,
                                        unit=self.unit
                                    )
                listCompressorFileData.append(imagesDirectoryCompress)
            else:
                listImagesData += images_directory

        if join:
            imagesDirectoryCompress = CompressorFileData(
                                        filename=name_directory,
                                        list_data=listImagesData,
                                        type=compressor,
                                        unit=self.unit
                                    )
            listCompressorFileData.append(imagesDirectoryCompress)

        if len(listCompressorFileData) == 0:
            return None
        return listCompressorFileData

    def files_by_level(
        self,
        listFiles: list
    ) -> dict:
        """
        Groups files by the first directory level, returns a dictionary with
        sorted directory names (keys) and file names (list of values).

        Args
            listFiles: list of name of files.

        Returns
            dict: dictionaries grouped by their container directory name.
        """
        results = {}

        levelDir = 0
        for item in listFiles:
            list_names = str(item.parent).split(self.separator)[-2:]

            if len(list_names) > 1:
                levelDir = 1

            dirKey = list_names[levelDir]

            # filename = str(item)
            if dirKey not in results:
                results[dirKey] = [item]
            else:
                results[dirKey].append(item)

        results = dict(sorted(results.items()))
        return results
