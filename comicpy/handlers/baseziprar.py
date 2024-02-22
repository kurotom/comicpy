# -*- coding: utf-8 -*-
"""
Base class for Hander ZIP and RAR.
"""

from comicpy.models import (
    CurrentFile,
    CompressorFileData
)

import os


class BaseZipRarHandler:
    """
    Base class for handler ZIP and RAR.
    """

    def to_write(
        self,
        currentCompressorFile: CompressorFileData,
        path: str
    ) -> dict:
        """
        Writes data to a CBR or CBZ file.

        Args:
            currentCompressorFile: `CompressorFileData` instance with the of
                                   list of ZIP or RAR files.
            path: location where the CBR or CBZ file will be stored.
                  Default `'.'`.

        Returns:
            dict: ZIP or RAR file information. Keys `'name'`, `'size'`.
        """
        info_compress = []
        data_to_write = currentCompressorFile.list_data

        if currentCompressorFile.join is False:
            for item in data_to_write:
                # print(type(item), item.name, item.extention)
                info = self.__write_data(
                            currentFile=item,
                            path=path
                        )
                info_compress.append(info)
        elif currentCompressorFile.join is True:
            data = currentCompressorFile.list_data[0]
            info = self.__write_data(
                            currentFile=data,
                            path=path
                        )
            info_compress.append(info)
        return info_compress

    def __write_data(
        self,
        currentFile: CurrentFile,
        path: str
    ) -> dict:
        """
        Write data into file.

        Args:
            currentFile: `CurrentFile` instance with data of ZIP or RAR file.
            path: location where the CBR or CBZ file will be stored.
                  Default `'.'`.

        Returns:
            dict: compressor file information. Keys `'name'`, `'size'`.
        """
        file_output = '%s%s' % (
                        currentFile.name,
                        currentFile.extention
                    )
        path_output = os.path.join(path, file_output)

        with open(path_output, 'wb') as file:
            file.write(currentFile.bytes_data.getvalue())

        return {
                'name': path_output,
                'size': '%.2f %s' % (
                                currentFile.size,
                                currentFile.unit.upper()
                            )
            }
