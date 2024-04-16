# -*- coding: utf-8 -*-
"""
ComicPy app
"""

from comicpy.comicpy import ComicPy

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
    ExtentionError,
    FileExtentionNotMatch,
    DirectoryPathNotExists,
    DirectoryFilterEmptyFiles,
    DirectoryEmptyFilesValid,
    InvalidCompressor
)

from comicpy.valid_extentions import ValidExtentions

from comicpy.handlers import (
    PdfHandler,
    ZipHandler,
    RarHandler,
    ImagesHandler
)

from comicpy.cli import CliComicPy
