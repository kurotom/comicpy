# -*- coding: utf-8 -*-
"""
Class in charge of getting the images from the page and converting them.

Used by PdfHandler.
"""

from comicpy.models import RawImage


from threading import Thread

from typing import Callable, TypeVar


Queue = TypeVar("Queue")
Document = TypeVar("fitz.Document")


class ThreadImage(Thread):

    def __init__(
        self,
        pagesgenerator: list,
        queue: Queue,
        uniques_hash: set,
        pdfDocument: Document,
        resize: str,
        to_image_instance_method: Callable[RawImage, str],
        daemon: bool = True
    ) -> None:
        """
        """
        Thread.__init__(self, daemon=daemon)
        self.pagesgenerator = pagesgenerator
        self.queue = queue
        self.uniques_hash = uniques_hash
        self.pdfDocument = pdfDocument
        self.to_image_instance_method = to_image_instance_method
        self.resize = resize

    def run(self) -> None:
        """
        Obtains the images and converts them.
        """
        raw_images= []
        for item in self.pagesgenerator:
            name = item[7]
            xref_image = item[0]

            raw_image = RawImage(
                                name=name,
                                xref_image=xref_image,
                            )

            imagen_data =  self.pdfDocument.extract_image(xref=xref_image)

            raw_image.data = imagen_data["image"]
            raw_image.extension = imagen_data["ext"]
            raw_image.get_md5()

            raw_images.append(raw_image)

        for raw_image in raw_images:
            if raw_image.md5 in self.uniques_hash:
                continue

            # print(raw_image)
            self.uniques_hash.add(raw_image.md5)

            image_comic = self.to_image_instance_method(
                                            rawimage=raw_image,
                                            resize=self.resize,
                                        )

            self.queue.put(image_comic)
