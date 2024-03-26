# -*- coding: utf-8 -*-
"""
Exceptions
"""


class UnitFileSizeInvalid(Exception):
    def __init__(
        self,
        message: str = 'Unit given is not valid.\n'
    ) -> None:
        message += 'Availables: "b", "kb", "mb", "gb".\n'
        super().__init__(message)


class ErrorFileBase(Exception):
    def __init__(
        self,
        message: str
    ) -> None:
        super().__init__(message)


class FilePasswordProtected(ErrorFileBase):
    def __init__(
        self,
        message: str
    ) -> None:
        message += '--> \t`password` parameter is required.'
        super().__init__(message)


class BadPassword(ErrorFileBase):
    def __init__(self) -> None:
        message = 'Incorrect Password.'
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


class DirectoryFilterEmptyFiles(ErrorFileBase):
    def __init__(
        self,
        dir_path: str,
        filter: str,
    ) -> None:
        message = 'Files not found with filter "%s" over directory "%s".' % (
                            filter,
                            dir_path
                        )
        super().__init__(message)


class DirectoryEmptyFilesValid(ErrorFileBase):
    def __init__(
        self,
        dir_path: str
    ) -> None:
        message = 'Not found valid files on "%s".\n' % (dir_path)
        message += 'Only files: .pdf, .cbz, .cbr.'
        super().__init__(message)
