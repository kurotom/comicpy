# -*- coding: utf-8 -*-
"""
"""

from pypdf import PdfReader, PdfWriter, PageObject
import io
import zipfile
import os

from typing import List


class ImageComicData:
    def __init__(
        self,
        name: str,
        bytes_data: bytes
    ) -> None:
        self.name = name
        self.bytes_data = bytes_data



class PdfToCbz:

    def __init__(
        self,
        pdf_path: str
    ) -> None:
        self.filename = pdf_path

    def convert_pdf_in_memory(self) -> io.BytesIO:
        """
        """
        pass

    def process(self):
        print('--> ', self.filename)
        reader = PdfReader(self.filename)
        # print(reader.metadata)
        # print(reader.pdf_header)
        print(len(reader.pages))

        # images_objs = self.getting_data(pages_pdf=reader.pages)
        # zipBytes = self.to_zip(listImageComicData=images_objs)
        # self.to_write(
        #     fileCBZ_path=self.filename.lower().replace('.pdf', '.cbz'),
        #     zipDataBytes=zipBytes
        # )

    def getting_data(
        self,
        pages_pdf: list
    ) -> List[ImageComicData]:
        data = []
        for i in range(len(pages_pdf)):
            page = pages_pdf[i]
            name_image = 'image%d.jpg'.zfill(4) % (i)
            image_comic = ImageComicData(
                            name=name_image,
                            bytes_data=io.BytesIO(page.images[0].data)
                        )
            data.append(image_comic)
        return data

    def to_zip(
        self,
        listImageComicData: ImageComicData
    ) -> io.BytesIO:
        buffer_data = io.BytesIO()
        with zipfile.ZipFile(
            file=buffer_data, mode='a',
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=False
        ) as zip_file:
            for item in listImageComicData:
                zip_file.writestr(item.name, item.bytes_data.getvalue())

        print(buffer_data.getbuffer().nbytes / 1000000)
        return buffer_data

    def to_write(
        self,
        fileCBZ_path: str,
        zipDataBytes: bytes
    ) -> None:
        with open(fileCBZ_path, 'wb') as file:
            file.write(zipDataBytes.getbuffer())
