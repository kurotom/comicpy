# -*- coding: utf-8 -*-
"""
Extentions valid for program.
"""


class ValidExtentions:

    PDF = '.pdf'
    CBR = '.cbr'
    CBZ = '.cbz'
    ZIP = '.zip'
    RAR = '.rar'
    JPEG = '.jpeg'
    PNG = '.png'
    JPG = '.jpg'
    WEBP = '.webp'

    def get_all_extentions(self) -> list:
        """
        Returns all valid extentions.
        """
        return [
            ValidExtentions.PDF,
            ValidExtentions.CBR,
            ValidExtentions.CBZ,
            ValidExtentions.ZIP,
            ValidExtentions.RAR,
            ValidExtentions.JPEG,
            ValidExtentions.PNG,
            ValidExtentions.JPG,
            ValidExtentions.WEBP
        ]

    def get_container_valid_extentions(self) -> list:
        """
        Returns valid extentions of content for RAR or ZIP files.
        """
        return [
                ValidExtentions.PDF,
                ValidExtentions.CBR,
                ValidExtentions.CBZ,
                ValidExtentions.ZIP,
                ValidExtentions.RAR
            ]

    def get_pdf_extention(self) -> str:
        """
        Returns valid pdf extention.
        """
        return ValidExtentions.PDF

    def get_images_extentions(self) -> list:
        """
        Returns valid extentions of images.
        """
        return [
                ValidExtentions.JPEG,
                ValidExtentions.PNG,
                ValidExtentions.JPG,
                ValidExtentions.WEBP
            ]

    def get_comic_extentions(self) -> list:
        """
        Returns valid extentions of comic files.
        """
        return [
            ValidExtentions.CBR,
            ValidExtentions.CBZ
        ]

    def get_compressors_extentions(self) -> list:
        """
        Returns valid extentions of compressors.
        """
        return [
                ValidExtentions.ZIP,
                ValidExtentions.RAR,
            ]
