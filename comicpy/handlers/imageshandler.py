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
    validFormats = {
        'JPEG': 'jpeg',
        'PNG': 'png',
        'JPG': 'jpeg'
    }
    sizeImageDict = {
        'sizeImage': None,
        'small': (800, 1200),
        'medium': (1000, 1500),
        'large': (1200, 1800),
    }

    def get_size(
        self,
        size: str = 'preserve'
    ) -> tuple:
        """
        Returns tupe of size.
        """
        try:
            return ImagesHandler.sizeImageDict[size]
        except KeyError:
            return ImagesHandler.sizeImageDict['small']

    def new_size_image(
        self,
        currentImage: Union[bytes, ImageInstancePIL],
        extention: str,
        sizeImage: str = 'preserve'
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
        size_tuple = self.get_size(size=sizeImage)
        newImageIO = io.BytesIO()

        if type(currentImage) is bytes:
            currentImage = Image.open(io.BytesIO(currentImage))

        if size_tuple is not None:
            imageResized = currentImage.resize(
                                    size_tuple,
                                    resample=Image.Resampling.LANCZOS
                                )
        imageResized.save(
                newImageIO,
                format=ImagesHandler.validFormats[extention],
                quality=90
            )
        return newImageIO
