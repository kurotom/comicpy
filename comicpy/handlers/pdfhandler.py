# -*- coding: utf-8 -*-
"""
"""

from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData
)

from pypdf import PdfReader

import io
import os

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
        listImageComicData = self.getting_data(pages_pdf=reader.pages)
        return listImageComicData

    def getting_data(
        self,
        pages_pdf: list
    ) -> List[ImageComicData]:
        data = []
        for i in range(len(pages_pdf)):
            page = pages_pdf[i]
            name_, extention_ = os.path.splitext(page.images[0].name)
            name_image = 'image' + '%d'.zfill(4) % (i) + extention_
            data_image = page.images[0].data
            # page.images[0].name, page.images[0].image
            image_comic = ImageComicData(
                            filename=name_image,
                            bytes_data=io.BytesIO(data_image)
                        )
            data.append(image_comic)
        return data
