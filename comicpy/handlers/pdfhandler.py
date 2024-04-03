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

from pypdf import PdfReader
import fitz

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

PYPDF = TypeVar('pypdf')
PYMUPDF = TypeVar('pymupdf')


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
        self.number_image = 1

    def reset_counter(self) -> None:
        """
        Resets the number of the image name counter.
        """
        self.number_image = 1

    def process_pdf(
        self,
        currentFilePDF: CurrentFile,
        compressor: str,
        is_join: bool = False,
        resizeImage: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve',
        motor: Union[PYPDF, PYMUPDF] = 'pypdf'
    ) -> Union[CompressorFileData, None]:
        """
        Takes the bytes from a PDF file and gets the images.

        Args:
            currentFilePDF: Instance of `CurrentFile` with the data of the PDF
                            file.
            compressor: type of compressor to use, RAR or ZIP.
            resizeImage: rescaling image.
            motor: motor to use, `pypdf` or `pymupdf`, default `pypdf`.

        Returns:
            List[ImageComicData]: list of instances of `ImageComicData` with
                                  the data of all the images in the PDF file.
        """
        listImageComicData = []

        if is_join is False:
            self.reset_counter()

        if motor == 'pypdf':
            listImageComicData = self.to_pypdf(
                                        filePDF=currentFilePDF,
                                        resize=resizeImage
                                    )
        elif motor == 'pymupdf':
            listImageComicData = self.to_pymupdf(
                                        filePDF=currentFilePDF,
                                        resize=resizeImage
                                    )

        if len(listImageComicData) == 0:
            return None
        # print(len(listImageComicData), type(listImageComicData[0]))
        pdfFileCompressor = CompressorFileData(
                                filename=currentFilePDF.name.replace(' ', '_'),
                                list_data=listImageComicData,
                                type=compressor,
                                unit=self.unit
                            )
        return pdfFileCompressor

    def to_pypdf(
        self,
        filePDF: CurrentFile,
        resize: str
    ) -> Union[List[ImageComicData], list]:
        """
        Gets images of the pages of a PDF file using PyPDF.
        Image comparison is performed by calculating the md5 hash by taking the
        original image name and its raw data. This method avoids duplicate
        images.
        The images are ordered using their name and numbering as a reference,
        in case of multiple images on a single page.

        Args:
            currentFilePDF: Instance of `CurrentFile` with the data of the PDF
                            file.
            resizeImage: rescaling image.

        Returns:
            List[ImageComicData]: list of `ImageComicData` instances with the
                                  page image data.
        """
        data = []
        reader = PdfReader(filePDF.bytes_data)
        pages_pdf = reader.pages
        n_pages = len(pages_pdf)
        i = 0
        dict_images = {}
        uniques_hash = []
        prev_images = 0
        # print(reader.pdf_header, n_pages, reader.metadata)

        while i < n_pages:
            # print(i, len(pages_pdf[i].images))

            if len(pages_pdf[i].images) > 0:
                try:
                    if len(pages_pdf[i].images) == 1:
                        item = pages_pdf[i].images[0]
                        hash_image = self.get_hash_md5(
                                                image_name=item.name,
                                                image_data=item.data,
                                            )
                        if hash_image not in uniques_hash:
                            uniques_hash.append(hash_image)

                            name_, extention_ = self.paths.splitext(item.name)
                            image_comic = self.to_image_instance(
                                dataImage=item.data,
                                extentionImage=extention_[1:],
                                resize=resize,
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

                                    name_, extention_ = self.paths.splitext(
                                                                    item.name
                                                                )
                                    image_comic = self.to_image_instance(
                                        dataImage=item.data,
                                        extentionImage=extention_[1:],
                                        resize=resize,
                                    )

                                    data.append(image_comic)
                        prev_images = len(pages_pdf[i].images)
                except OSError as e:
                    # Skip truncated images.
                    print('Skipped truncated image, page "%d".' % (i))
                    pass

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
        dataImage: bytes,
        extentionImage: str,
        resize: str,
        current_image: ImageInstancePIL = None,
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
        name_image = 'Image%s.%s' % (
                            str(self.number_image).zfill(4),
                            extentionImage.lower()
                        )
        # print(index, current_image.name, name_image)
        image_comic = self.imageshandler.new_image(
                                name_image=name_image,
                                currentImage=dataImage,
                                extention=extentionImage.upper(),
                                sizeImage=resize,
                                unit=self.unit
                            )

        self.number_image += 1
        return image_comic

    def to_pymupdf(
        self,
        filePDF: CurrentFile,
        resize: str = 'preserve'
    ) -> Union[List[ImageComicData], list]:
        """
        Gets images of the pages of a PDF file using PyMuPDF.

        Args:
            currentFilePDF: Instance of `CurrentFile` with the data of the PDF
                            file.
            resizeImage: rescaling image.

        Returns:
            List[ImageComicData]: list of `ImageComicData` instances with the
                                  page image data.
        """

        list_images = []

        pdf_doc = fitz.open(stream=filePDF.bytes_data, filetype='pdf')

        for i in range(len(pdf_doc)):
            page = pdf_doc[i]
            for indx, image in enumerate(page.get_images(full=True)):
                refImage = image[0]
                image_base = pdf_doc.extract_image(refImage)

                image_data = image_base['image']
                image_extention = image_base['ext']

                image_comic = self.to_image_instance(
                    dataImage=image_data,
                    extentionImage=image_extention,
                    resize=resize,
                )
                list_images.append(image_comic)

                self.number_image += 1
        return list_images
