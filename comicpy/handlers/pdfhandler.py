# -*- coding: utf-8 -*-
"""
Handler related to files ZIP.
"""

from comicpy.handlers.imageshandler import ImagesHandler
from comicpy.utils import Paths

from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData
)

from pypdf import (
    PdfReader,
    PageObject
)

from typing import (
    List,
    TypeVar,
    Union
)

import re
from hashlib import md5


PRESERVE = TypeVar('preserve')
SMALL = TypeVar('small')
MEDIUM = TypeVar('medium')
LARGE = TypeVar('large')
ImageInstancePIL = TypeVar("ImageInstancePIL")


class PdfHandler:
    """
    Class in charge of extract images from PDF file.
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
        self.number_image = 0

    def reset_counter(self) -> None:
        """
        Resets the number of the image name counter.
        """
        self.number_image = 0

    def process_pdf(
        self,
        currentFilePDF: CurrentFile,
        compressor: str,
        resizeImage: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> Union[CompressorFileData, None]:
        """
        Takes the bytes from a PDF file and gets the images.

        Args:
            currentFilePDF: Instance of `CurrentFile` with the data of the PDF
                            file.

        Returns:
            List[ImageComicData]: list of instances of `ImageComicData` with
                                  the data of all the images in the PDF file.
        """
        self.reset_counter()

        dataRaw = currentFilePDF.bytes_data
        reader = PdfReader(dataRaw)
        # print(reader.pdf_header, len(reader.pages), reader.metadata)
        listImageComicData = self.getting_data(
                                    pages_pdf=reader.pages,
                                    resize=resizeImage
                                )
        if len(listImageComicData) == 0:
            return None
        # print(len(listImageComicData))
        pdfFileCompressor = CompressorFileData(
                                filename=currentFilePDF.name.replace(' ', '_'),
                                list_data=listImageComicData,
                                type=compressor,
                                unit=self.unit
                            )
        return pdfFileCompressor

    def getting_data(
        self,
        pages_pdf: List[PageObject],
        resize: str
    ) -> Union[List[ImageComicData], list]:
        """
        Gets images of the pages of a PDF file.
        Image comparison is performed by calculating the md5 hash by taking the
        original image name and its raw data. This method avoids duplicate
        images.
        The images are ordered using their name and numbering as a reference,
        in case of multiple images on a single page.

        Args:
            pages_pdf: list of `PageObject` objects of the PDF file.

        Returns:
            List[ImageComicData]: list of `ImageComicData` instances with the
                                  page image data.
        """
        data = []
        n_pages = len(pages_pdf)
        i = 0
        dict_images = {}
        uniques_hash = []
        prev_images = 0
        while i < n_pages:
            # print(len(pages_pdf[i].images))

            if len(pages_pdf[i].images) == 0:
                pass
            else:

                if len(pages_pdf[i].images) == 1:
                    item = pages_pdf[i].images[0]
                    hash_image = self.get_hash_md5(
                                            image_name=item.name,
                                            image_data=item.data,
                                        )
                    if hash_image not in uniques_hash:
                        uniques_hash.append(hash_image)
                        image_comic = self.to_image_instance(
                                            current_image=item,
                                            resize=resize
                                        )
                        data.append(image_comic)

                elif len(pages_pdf[i].images) > 1:
                    # original order must be preserve
                    if prev_images != len(pages_pdf[i].images):
                        list_numeration = self.get_numbers_images(
                                                list_data=pages_pdf[i].images
                                            )

                        dict_images = dict(
                                            zip(
                                                list_numeration,
                                                pages_pdf[i].images
                                            )
                                        )
                        sorted_dict = dict(sorted(dict_images.items()))
                        for key, item in sorted_dict.items():
                            hash_image = self.get_hash_md5(
                                                    image_name=item.name,
                                                    image_data=item.data,
                                                )
                            if hash_image not in uniques_hash:
                                uniques_hash.append(hash_image)
                                image_comic = self.to_image_instance(
                                                    current_image=item,
                                                    resize=resize
                                                )
                                data.append(image_comic)
                    prev_images = len(pages_pdf[i].images)

            i += 1

        return data

    def get_hash_md5(
        self,
        image_name: str,
        image_data: bytes
    ) -> str:
        """
        Calculates hash md5.

        Args
            image_name: name of image.
            image_data: raw data of image.

        Returns
            str: hash md5 string.
        """
        hash_data = image_name.encode() + image_data
        return md5(hash_data).hexdigest()

    def get_numbers_images(
        self,
        list_data: list
    ) -> list:
        """
        Gets numeration of images on image names.
        Records the name and size of the image data to avoid duplicate images.

        Args
            list: list of images of pages.

        Returns
            list: list of numbers of images.
        """
        result = []
        for item in list_data:
            r = re.split(r'([0-9]{1,4})', item.name)
            if r is not None:
                number = [int(i) for i in r if i.isdigit()][0]
                result.append(number)
        return result

    def to_image_instance(
        self,
        current_image: ImageInstancePIL,
        resize: str,
    ) -> ImageComicData:
        """
        Creates an image instance with new dimensions and names, preserving the
        data.

        Args
            current_image: `PIL.Image` instance.
            resize: string of new size of image.

        Returns
            ImageComicData: instance with byte data, new name.
        """
        name_, extention_ = self.paths.splitext(current_image.name)
        # name_image = 'Image' + str(index).zfill(4) + extention_.lower()
        name_image = 'Image%s%s' % (
                            str(self.number_image).zfill(4),
                            extention_.lower()
                        )
        # print(index, current_image.name, name_image)
        image_comic = self.imageshandler.new_image(
                                name_image=name_image,
                                currentImage=current_image.image,
                                extention=extention_[1:].upper(),
                                sizeImage=resize,
                                unit=self.unit
                            )
        image_comic.original_name = current_image.name
        self.number_image += 1
        return image_comic
