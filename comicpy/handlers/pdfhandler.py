# -*- coding: utf-8 -*-
"""
Handler related to files ZIP.
"""

from comicpy.handlers.imageshandler import ImagesHandler
from comicpy.handlers.pdfhandler_thread import ThreadImage

from comicpy.utils import Paths

from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData,
    RawImage,
)



from typing import (
    List,
    TypeVar,
    Union,
    Callable
)

import re
from queue import Queue

import fitz

import logging


PRESERVE = TypeVar('preserve')
SMALL = TypeVar('small')
MEDIUM = TypeVar('medium')
LARGE = TypeVar('large')
ImageInstancePIL = TypeVar("ImageInstancePIL")

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
        self.number_image = 1
        # handle log messages PyMuPDF.
        self.logger = logging.getLogger("pymupdf")
        self.logger.setLevel(logging.ERROR)

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
        motor: Union[PYMUPDF] = 'pymupdf',
        show_progress: bool = False
    ) -> Union[CompressorFileData, None]:
        """
        Takes the bytes from a PDF file and gets the images.

        Args:
            currentFilePDF: Instance of `CurrentFile` with the data of the PDF
                            file.
            compressor: type of compressor to use, RAR or ZIP.
            resizeImage: rescaling image.
            motor: motor to use, `pymupdf` default `pymupdf`.

        Returns:
            List[ImageComicData]: list of instances of `ImageComicData` with
                                  the data of all the images in the PDF file.
        """
        listImageComicData = []

        if is_join is False:
            self.reset_counter()


        listImageComicData = self.to_pymupdf(
                                        filePDF=currentFilePDF,
                                        resize=resizeImage,
                                        show_progress=show_progress
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

    def to_pymupdf(
        self,
        filePDF: CurrentFile,
        resize: str,
        n_threads: int = 4,
        show_progress: bool = False,
    ) -> Union[List[ImageComicData], list]:
        """
        Gets images of the pages of a PDF file using PyMuPDF.
        Image comparison is performed by calculating the md5 hash by taking the
        original image name and its raw data. This method avoids duplicate
        images.
        The images are ordered using their name and numbering as a reference,
        in case of multiple images on a single page.

        Args:
            filePDF: Instance of `CurrentFile` with the PDF file data.
            resize: string to resize the image.
            n_threads: number of threads to get the images of the PDF pages,
                       default 4.
            show_progress: boolean to show the progress of the current PDF file,
                           default False.

        Returns:
            List[ImageComicData]: list of `ImageComicData` instances with the
                                  page image data.
        """
        data = []
        uniques_hash = set()
        queue_images = Queue()

        # minimum images per chunk of the image list, it is arbitrary
        minimum_images_by_page = 30

### PYMUPDF
        pdf_file = fitz.open("pdf", filePDF.bytes_data)
        # print(pdf_file.page_count, "\n")
        n_pages = pdf_file.page_count


#### THREADs
        for page in pdf_file.pages():
            if show_progress:
                print(f"\r>>> Page: {page.number + 1}/{n_pages}", end="", flush=True)

            threads_list = []
            # sorts the images by number in the names.
            images = sorted(
                        page.get_images(),
                        key=lambda x: self.get_number_image(name=x[7])
                    )

            # determines the number of images per chunk of the list,
            # used by the threads.

            n_images = len(images) // n_threads

            if n_images < minimum_images_by_page:
                th = ThreadImage(
                            pagesgenerator=images,
                            uniques_hash=uniques_hash,
                            queue=queue_images,
                            pdfDocument=pdf_file,
                            to_image_instance_method=self.to_image_instance,
                            resize=resize
                        )
                threads_list.append(th)
                th.start()
                th.join()
            else:
                for i in range(0, len(images) + 1, n_images):
                    chunk = images[i: i + n_images]

                    th = ThreadImage(
                                pagesgenerator=chunk,
                                uniques_hash=uniques_hash,
                                queue=queue_images,
                                pdfDocument=pdf_file,
                                to_image_instance_method=self.to_image_instance,
                                resize=resize
                            )
                    threads_list.append(th)
                    th.start()

                    # print(">>> threads_list", len(threads_list))
                    for t in threads_list:
                        t.join()

        list_images_unique = list(queue_images.queue)
        data = list_images_unique
#### THREADs
        if show_progress:
            print('\n')
        return data

    def get_number_image(
        self,
        name: str
    ) -> int:
        """
        Gets number of image in name.

        Args
            name: string of name of image.

        Returns
            int: integer of name of image.
        """
        res = re.search(r"(\d+)", name)
        return int(res.group(1))

    def to_image_instance(
        self,
        rawimage: RawImage,
        resize: str,
    ) -> ImageComicData:
        """
        Creates an image instance with new dimensions and names, preserving the
        data.

        Args
            rawimage: `RawImage` instance.
            resize: string of new size of image.

        Returns
            ImageComicData: instance with byte data, new name.
        """
        name_image = 'Image%s.%s' % (
                            str(self.number_image).zfill(4),
                            rawimage.extension.lower()
                        )
        # print(rawimage)
        image_comic = self.imageshandler.new_image(
                                name_image=name_image,
                                currentImage=rawimage.data,
                                extension=rawimage.extension.upper(),
                                sizeImage=resize,
                                unit=self.unit
                            )

        self.number_image += 1
        return image_comic
