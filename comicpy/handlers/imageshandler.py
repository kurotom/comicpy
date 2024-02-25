# -*- coding: utf-8 -*-
"""
`ImageComicData` handles image-related issues, such as resizing, resizing in
the future, formatting, and other related issues, if required.
"""

from PIL import Image
import io

from typing import TypeVar, Union

ImageInstancePIL = TypeVar("ImageInstancePIL")


class ImagesHandler:
    """
    Class dealing with image issues, such as resizing.
    """

    extentionsImage = {
        '.PNG': 'PNG',
        '.JPEG': 'JPEG',
        '.JPG': 'JPEG'
    }

    sizeImageDict = {
        'small': (800, 1200),
        'medium': (1000, 1500),
        'large': (1200, 1800),
    }

    def new_size_image(
        self,
        currentImage: Union[bytes, ImageInstancePIL],
        extention: str,
        sizeImage: str = 'small'
    ) -> io.BytesIO:
        """
        Resize image.

        Args:
            currentImage: `PIL` instance with data of original image.
            extension: extention of original image.
            sizeImage: category of size to resize original image. Default is
                       'small'.

        Returns:
            io.BytesIO: `BytesIO` instance with data of new resized image.
        """
        newImageIO = io.BytesIO()
        if type(currentImage) is bytes:
            currentImage = Image.open(io.BytesIO(currentImage))

        size_tuple = ImagesHandler.sizeImageDict[sizeImage]
        imageResized = currentImage.resize(size_tuple)
        imageResized.save(
                newImageIO,
                format=ImagesHandler.extentionsImage[extention]
            )
        return newImageIO
