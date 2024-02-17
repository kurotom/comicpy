# -*- coding: utf-8 -*-
"""
"""

from comicpy.models import (
    ImageComicData,
    CurrentFile
)

from pypdf import PdfReader, PdfWriter, PageObject

from PIL import Image
import io

from typing import List, TypeVar

CurrentFileInstance = TypeVar('CurrentFileInstance')


class PdfHandler:

    def process_pdf(
        self,
        currentFilePDF: CurrentFileInstance
    ) -> List[ImageComicData]:
        dataRaw = currentFilePDF.bytes_data
        reader = PdfReader(dataRaw)
        # print(reader.pdf_header, len(reader.pages), reader.metadata)
        images_objs = self.getting_data(pages_pdf=reader.pages)
        return images_objs

    def getting_data(
        self,
        pages_pdf: list
    ) -> List[ImageComicData]:
        data = []
        for i in range(len(pages_pdf)):
            page = pages_pdf[i]
            name_image = 'image' + '%d'.zfill(4) % (i) + '.jpg'
            data_image = page.images[0].data
            # page.images[0].name
            # page.images[0].image
            image_comic = ImageComicData(
                            filename=name_image,
                            bytes_data=io.BytesIO(data_image)
                        )
            data.append(image_comic)
        return data
