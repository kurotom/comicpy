# -*- coding: utf-8 -*-
"""
Extensions valid for program.
"""


class ValidExtensions:

    PDF = '.pdf'
    CBR = '.cbr'
    CBZ = '.cbz'
    ZIP = '.zip'
    RAR = '.rar'
    JPEG = '.jpeg'
    PNG = '.png'
    JPG = '.jpg'
    WEBP = '.webp'

    def get_all_extensions(self) -> list:
        """
        Returns all valid extensions.
        """
        return [
            ValidExtensions.PDF,
            ValidExtensions.CBR,
            ValidExtensions.CBZ,
            ValidExtensions.ZIP,
            ValidExtensions.RAR,
            ValidExtensions.JPEG,
            ValidExtensions.PNG,
            ValidExtensions.JPG,
            ValidExtensions.WEBP
        ]

    def get_container_valid_extensions(self) -> list:
        """
        Returns valid extensions of content for RAR or ZIP files.
        """
        return [
                ValidExtensions.PDF,
                ValidExtensions.CBR,
                ValidExtensions.CBZ,
                ValidExtensions.ZIP,
                ValidExtensions.RAR,
                ValidExtensions.JPEG,
                ValidExtensions.PNG,
                ValidExtensions.JPG,
                ValidExtensions.WEBP
            ]

    def get_pdf_extension(self) -> str:
        """
        Returns valid pdf extension.
        """
        return ValidExtensions.PDF

    def get_images_extensions(self) -> list:
        """
        Returns valid extensions of images.
        """
        return [
                ValidExtensions.JPEG,
                ValidExtensions.PNG,
                ValidExtensions.JPG,
                ValidExtensions.WEBP
            ]

    def get_comic_extensions(self) -> list:
        """
        Returns valid extensions of comic files.
        """
        return [
            ValidExtensions.CBR,
            ValidExtensions.CBZ
        ]

    def get_compressors_extensions(self) -> list:
        """
        Returns valid extensions of compressors.
        """
        return [
                ValidExtensions.ZIP,
                ValidExtensions.RAR,
            ]
