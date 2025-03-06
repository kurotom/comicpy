# -*- coding: utf-8 -*-
"""
Models
"""

import io
import re
from hashlib import md5


from comicpy.utils import (
    SizeUnits,
    Paths
)


from typing import List, Union, TypeVar


RawImage = TypeVar("RawImage")


class RawImage:
    """
    Class in charge for keep data of a raw image.
    """
    def __init__(
        self,
        name: str,
        xref_image: int,
        data: Union[bytes, io.BytesIO] = None,
        page: int = 0
    ) -> None:
        """
        """
        self.name = name
        self.extension : str = None
        self.data = data
        self.md5 = ""
        self.page = page
        self.id = self.get_number_image(name=self.name)

    def get_number_image(
        self,
        name: str
    ) -> int:
        """
        Gets number of image in name.
        """
        res = re.search(r"(\d+)", name)
        return int(res.group(1))

    def get_extension(
        self,
        name: str
    ) -> tuple:
        """
        Gets extension of image.
        """
        name_, extension_ = Paths.splitext(name)
        return extension_.lower()[1:]

    def get_md5(
        self,
    ) -> None:
        """
        Sets the md5 attribute from the RawImage instance data.
        """
        self.md5 = md5(self.data).hexdigest()

    def __lt__(
        self,
        other: RawImage
    ) -> bool:
        """
        Returns
            bool: if self is less than other `RawImage`.
        """
        return self.id < other.id

    def __hash__(self) -> int:
        """
        Returns
            int: integer calculated from the md5 hash.
        """
        return int(self.md5, 16)

    def __eq__(
        self,
        other: RawImage
    ) -> bool:
        """
        Returns
            bool: if self and other `RawImage` is equal.
        """
        if isinstance(other, RawImage):
            return self.md5 == other.md5
        return False

    def __str__(self) -> str:
        """
        Returns
            str: represents instance.
        """
        return "RawImage: %d, %s" % (self.name, self.md5)

    def __repr__(self) -> str:
        """
        Representation of instance.

        Returns
            str: represents instance.
        """
        return "<[ %s ]>" % self.__str__()


class FileBaseClass:
    """
    Base class
    """

    def get_extension(
        self,
    ) -> None:
        """
        Gets name and extension from file name.
        Sets attributes `name` and `extension`.
        """
        file_name = Paths.get_basename(self.filename)
        name_, extension_ = Paths.splitext(file_name)
        self.name = name_
        if self.extension is None:
            self.extension = extension_.lower()

    def get_size(
        self,
    ) -> int:
        """
        Gets size of data, and set `size` attribute.

        Returns
            int: data size value.
        """
        try:
            size_unit = SizeUnits[self.unit]
        except KeyError:
            self.unit = 'mb'
            size_unit = SizeUnits[self.unit]
        size_buffer = self.bytes_data.getbuffer().nbytes / size_unit
        return size_buffer

    def __str__(self) -> str:
        """
        Returns
            str: represents instance.
        """
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Representation of instance.

        Returns
            str: represents instance.
        """
        return '<[Filename: "%s", Size: "%.2f %s"]>' % (
                        self.filename,
                        self.size,
                        self.unit.upper()
                )


class ImageComicData(FileBaseClass):
    """
    Class in charge of keep data of images.
    """

    def __init__(
        self,
        filename: str,
        bytes_data: io.BytesIO,
        extension: str = None,
        unit: str = 'mb'
    ) -> None:
        """
        Constructor

        Args:
            filename: str, file name of image.
            bytes_data: bytes, raw data of image.
            extension: extension of image.
            unit: unit measure of data.
        """
        self.filename = filename
        self.extension = extension
        self.bytes_data = bytes_data
        self.name = None
        self.is_comic = False
        self.unit = unit
        self.original_name = None
        self.size = super().get_size()
        super().get_extension()

    def __str__(self) -> str:
        """
        Representation of instance.

        Returns
            str: represents instance.
        """
        return super().__str__()


class CurrentFile(FileBaseClass):
    """
    Class in charge for saving data of file.
    """

    def __init__(
        self,
        filename: str,
        bytes_data: io.BytesIO,
        chunk_bytes: bytes = None,
        extension: str = None,
        is_comic: bool = False,
        unit: str = 'mb'
    ) -> None:
        """
        Constructor

        Args:
            filename: name of a file.
            bytes_data: raw data of a file.
            chunk_bytes: first 16 bytes of file data.
            extension: file extension.
            unit: unit of measurement of data size.
        """
        self.filename = filename
        self.extension = extension
        self.is_comic = is_comic
        self.chunk_bytes = chunk_bytes
        self.bytes_data = bytes_data
        self.name = None
        self.path = None
        self.unit = unit
        self.size = super().get_size()
        super().get_extension()

    def __str__(self) -> str:
        """
        Representation of instance.

        Returns
            str: represents instance.
        """
        return super().__str__()


class CompressorFileData(FileBaseClass):
    """
    Class responsible for saving the data of a RAR or ZIP compressor.
    """
    def __init__(
        self,
        filename: str,
        list_data: Union[List[ImageComicData], List[CurrentFile]],
        type: str,
        join: bool = False,
        unit: str = 'mb'
    ) -> None:
        """
        Constructor

        Args:
            filename: filename of the file.
            list_data: list of `ImageComicData` instances with the image data
                       or list of `CurrentFile` instances with data from
                       individual RAR or ZIP archives.
            type: type of compressor used.
            unit: unit of measure of the data size.
        """
        self.filename = filename
        self.list_data = list_data
        self.type = type
        self.join = join
        self.items = 0
        self.extension = None
        self.unit = unit
        self.size = 0
        self.set_items()
        self.get_size()

    def set_items(self) -> None:
        self.items = len(self.list_data)

    def setExtension(self) -> str:
        """
        Sets `extension` attribute.

        Returns
            str: extension.
        """
        if self.type[0] != '.':
            self.extension = '.%s' % (self.type)
        else:
            self.extension = self.type

    def get_extension(self) -> None:
        """
        Overwrites the parent method, does nothing.
        """
        pass

    def get_size(self) -> int:
        """
        Calculates the size of the information based on the established unit of
        measurement.

        Returns
            int: size of file.

        Raises:
            KeyError: if unit measure is invalid.
        """
        try:
            size_unit = SizeUnits[self.unit]
        except KeyError:
            self.unit = 'mb'
            size_unit = SizeUnits[self.unit]

        sizes = [
            item.bytes_data.getbuffer().nbytes
            for item in self.list_data
        ]

        self.size = sum(sizes) / size_unit

    def __len__(self) -> int:
        return len(self.list_data)

    def __str__(self) -> str:
        """
        Returns
            str: represents instance.
        """
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Representation of instance.

        Returns
            str: represents instance.
        """
        return '<[Filename: "%s", Size: "%.2f %s", Items: "%s"]>' % (
                        self.filename,
                        self.size,
                        self.unit.upper(),
                        self.items
                )
