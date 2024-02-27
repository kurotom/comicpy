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

    def process_pdf(
        self,
        currentFilePDF: CurrentFile,
        compressor: str,
        resizeImage: Union[PRESERVE, SMALL, MEDIUM, LARGE] = 'preserve'
    ) -> CompressorFileData:
        """
        Takes the bytes from a PDF file and gets the images.

        Args:
            currentFilePDF: Instance of `CurrentFile` with the data of the PDF
                            file.

        Returns:
            List[ImageComicData]: list of instances of `ImageComicData` with
                                  the data of all the images in the PDF file.
        """
        dataRaw = currentFilePDF.bytes_data
        reader = PdfReader(dataRaw)
        # print(reader.pdf_header, len(reader.pages), reader.metadata)
        # print(len(reader.pages))
        listImageComicData = self.getting_data(
                                    pages_pdf=reader.pages,
                                    resize=resizeImage
                                )
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
    ) -> List[ImageComicData]:
        """
        Gets images of the pages of a PDF file.

        Args:
            pages_pdf: list of `PageObject` objects of the PDF file.

        Returns:
            List[ImageComicData]: list of `ImageComicData` instances with the
                                  page image data.
        """
        data = []
        n_pages = len(pages_pdf)
        i = 0
        while i < n_pages:
            # print(i, len(pages_pdf[i].images))
            if len(pages_pdf[i].images) == 1:
                current_image = pages_pdf[i].images[0]
            elif len(pages_pdf[i].images) > 1:
                current_image = pages_pdf[i].images[i]

            name_, extention_ = self.paths.splitext(current_image.name)
            name_image = 'Image' + '%d'.zfill(4) % (i) + extention_.lower()

            imageIO = self.imageshandler.new_size_image(
                                    currentImage=current_image.image,
                                    extention=extention_[1:].upper(),
                                    sizeImage=resize
                                )

            # print(images[i].name, name_image)
            image_comic = ImageComicData(
                            filename=name_image,
                            bytes_data=imageIO,
                            unit=self.unit
                        )
            data.append(image_comic)

            i += 1

        return data
