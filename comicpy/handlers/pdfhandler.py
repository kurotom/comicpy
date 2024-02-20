# -*- coding: utf-8 -*-
"""
Handler related to files ZIP.
"""

from comicpy.models import (
    ImageComicData,
    CurrentFile
)

from pypdf import (
    PdfReader,
    PageObject
)

import io
import os

from typing import List


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

    def process_pdf(
        self,
        currentFilePDF: CurrentFile
    ) -> List[ImageComicData]:
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
        listImageComicData = self.getting_data(pages_pdf=reader.pages)
        return listImageComicData

    def getting_data(
        self,
        pages_pdf: List[PageObject]
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
        for i in range(len(pages_pdf)):
            page = pages_pdf[i]
            name_, extention_ = os.path.splitext(page.images[0].name)
            name_image = 'image' + '%d'.zfill(4) % (i) + extention_
            data_image = page.images[0].data
            # page.images[0].name, page.images[0].image
            image_comic = ImageComicData(
                            filename=name_image,
                            bytes_data=io.BytesIO(data_image),
                            unit=self.unit
                        )
            data.append(image_comic)
        return data
