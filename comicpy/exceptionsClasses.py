# -*- coding: utf-8 -*-
"""
Exceptions
"""


class ErrorFileBase(Exception):
    def __init__(
        self,
        message: str
    ) -> None:
        super().__init__(message)


class InvalidFile(ErrorFileBase):
    def __init__(
        self,
        message: str = 'File given is invalid!'
    ) -> None:
        super().__init__(message)


class EmptyFile(ErrorFileBase):
    def __init__(
        self,
        message: str = 'File is empty!'
    ) -> None:
        super().__init__(message)


class FileExtentionNotMatch(ErrorFileBase):
    def __init__(
        self,
        message: str = 'File content does not match with extension of file!\n'
    ) -> None:
        message += '''
        Possibly the extension of the original file has changed manually.
        '''
        super().__init__(message)


class DirectoryPathNotExists(ErrorFileBase):
    def __init__(
        self,
        dir_path: str
    ) -> None:
        message = 'Directory "%s" not exist.' % (dir_path)
        super().__init__(message)


class DirectoryEmptyFilesValid(ErrorFileBase):
    def __init__(
        self,
        dir_path: str
    ) -> None:
        message = 'Not found valid files on "%s".\n' % (dir_path)
        message += 'Only files: .pdf, .cbz, .cbr.'
        super().__init__(message)
