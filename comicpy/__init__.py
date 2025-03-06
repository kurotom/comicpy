# -*- coding: utf-8 -*-
"""
ComicPy app
"""

from comicpy.comicpycontroller import ComicPy

from comicpy.models import (
    ImageComicData,
    CurrentFile,
    CompressorFileData
)

from comicpy.checkfile import CheckFile

from comicpy.exceptionsClasses import (
    UnitFileSizeInvalid,
    ErrorFileBase,
    FilePasswordProtected,
    BadPassword,
    InvalidFile,
    EmptyFile,
    ExtensionError,
    FileExtensionNotMatch,
    DirectoryPathNotExists,
    DirectoryFilterEmptyFiles,
    DirectoryEmptyFilesValid,
    InvalidCompressor
)

from comicpy.valid_extensions import ValidExtensions

from comicpy.handlers import (
    PdfHandler,
    ZipHandler,
    RarHandler,
    ImagesHandler
)

from comicpy.cli import CliComicPy
