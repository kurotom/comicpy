# -*- coding: utf-8 -*-
"""
"""

from pypdf import PdfReader, PdfWriter, PageObject
import io
import zipfile




class PdfToCbz:

    def __init__(
        self,
        pdf_path: str
    ) -> None:
        self.pdf_path = pdf_path

    def convert_pdf_in_memory(self) -> io.BytesIO:
        """
        """
        # bytes_io = io.BytesIO()
        # with open(self.pdf_path, 'rb') as file:
        #     data = file.read()
        pages = []
        with zipfile.ZipFile(self.pdf_path, 'r') as fileZ:
            pages_files = fileZ.namelist()
            for file_image in pages_files:
                if file_image.endswith('jpg'):
                    data = io.BytesIO()
                    data.write(fileZ.read(file_image))
                    pages.append(data)
                    break

        # with open('f.jpg', 'wb') as fl:
        #     fl.write(data.getbuffer())

        writer = PdfWriter()
        for i in range(len(pages)):
            # writer.write('f.jpg')
            writer.insert_page(pages[i], index=i)
            # pages[i].close()
        writer.write('final.pdf')
        # writer.write(bytes_io)
        # # bytes_io.write(writer)
        # writer.write_stream(bytes_io)
        # print(bytes_io.getbuffer().nbytes)
        # return bytes_io

    def process(self):
        print('--> ', self.pdf_path)
        data_bytes_io = self.convert_pdf_in_memory()
        # reader = PdfReader(data_bytes_io)
        # print(reader.pdf_header)
        # print(len(reader.pages))
        # for page in reader.pages:
        #     print(page)
        #
        # data_bytes_io.close()



        # writer = PdfWriter(fileobj=data)
        # writer.write('final.pdf')



if __name__ == '__main__':
    file = 'FNAE CAPS 01-04 (TOMO1).PDF'
    file = 'Yamada-Kun To 7-Nin No Majo Tomo 01.pdf'
    pdf = PdfToCbz(pdf_path=file)
    pdf.process()
