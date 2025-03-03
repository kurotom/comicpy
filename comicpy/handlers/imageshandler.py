# -*- coding: utf-8 -*-
"""
`ImageComicData` handles image-related issues, such as resizing, resizing in
the future, formatting, and other related issues, if required.

Options for resize images.
* 'preserve' :  original size.
* 'small'     :  800 x 1200.
* 'medium'    :  1000 x 1500.
* 'large'     :  1200 x 1800.
"""


from comicpy.models import ImageComicData

from comicpy.valid_extensions import ValidExtensions

from PIL import Image
import io

from typing import TypeVar, Union

ImageInstancePIL = TypeVar("ImageInstancePIL")


class ImagesHandler:
    """
    Class dealing with image issues, such as resizing.
    """
    validFormats = {
        'JPEG': ValidExtensions.JPEG[1:],
        'PNG': ValidExtensions.PNG[1:],
        'JPG': ValidExtensions.JPG[1:],
        'WEBP': ValidExtensions.WEBP[1:]
    }
    sizeImageDict = {
        'preserve': None,
        'small': (800, 1200),
        'medium': (1000, 1500),
        'large': (1200, 1800),
    }

    def get_size(
        self,
        size: str = 'preserve'
    ) -> tuple:
        """
        Returns tuple of size.

        Args
            size: string indicating the new size of the image.

        Returns
            tuple: tuple of int.
        """
        try:
            return ImagesHandler.sizeImageDict[size]
        except KeyError:
            return ImagesHandler.sizeImageDict['small']

    def get_format(
        self,
        extension_img: str
    ) -> str:
        """
        Returns image extension.

        Args
            extension_img: original extension of image.

        Returns
            str: image extension.
        """
        try:
            if extension_img == 'JPG' or extension_img == 'JP2':
                extension_img = 'JPEG'
            return ImagesHandler.validFormats[extension_img]
        except KeyError:
            return ImagesHandler.validFormats['JPEG']

    def new_image(
        self,
        name_image: str,
        currentImage: Union[bytes, ImageInstancePIL],
        extension: str,
        unit: str,
        sizeImage: str = 'preserve',
    ) -> ImageComicData:
        """
        Resize image.

        Args:
            name_image: name of image.
            currentImage: `PIL` instance with data of original image.
            extension: extension of original image.
            unit: unit of measure data.
            sizeImage: category of size to resize original image. Default is
                       'small'.

        Returns:
            ImageComicData: `ImageComicData` instance with data of image.
        """
        # print(name_image, extension, type(currentImage))
        size_tuple = self.get_size(size=sizeImage)
        newImageIO = io.BytesIO()

        if type(currentImage) is bytes:
            currentImage = Image.open(io.BytesIO(currentImage))

        # force image color, RGB.
        currentImage = currentImage.convert('RGB')

        if size_tuple is not None:
            imageResized = currentImage.resize(
                                    size_tuple,
                                    resample=Image.Resampling.LANCZOS
                                )
        else:
            imageResized = currentImage

        imageResized.save(
                newImageIO,
                format=self.get_format(extension_img=extension),
                # quality=90
                quality=100
            )

        image_comic = ImageComicData(
                        filename=name_image,
                        bytes_data=newImageIO,
                        unit=unit
                    )
        return image_comic
