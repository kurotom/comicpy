# -*- coding: utf-8 -*-
"""
Base class for Hander ZIP and RAR.
"""

from comicpy.models import (
    CurrentFile,
    CompressorFileData
)


class BaseZipRarHandler:
    """
    Base class for handler ZIP and RAR.
    """

    def to_write(
        self,
        currentCompressorFile: CompressorFileData
    ) -> dict:
        """
        Writes data to a CBR or CBZ file.

        Args:
            CurrentFile: instance with the data in the ZIP or RAR file.

        Returns:
            dict: ZIP or RAR file information. Keys `'name'`, `'size'`.
        """
        info_compress = []
        data_to_write = currentCompressorFile.list_data

        if currentCompressorFile.join is False:
            for item in data_to_write:
                # print(type(item), item.name, item.extention)
                info = self.__write_data(currentCompressorFile=item)
                info_compress.append(info)
        elif currentCompressorFile.join is True:
            data = currentCompressorFile.list_data[0]
            info = self.__write_data(currentCompressorFile=data)
            info_compress.append(info)
        return info_compress

    def __write_data(
        self,
        currentCompressorFile: CurrentFile
    ) -> dict:
        """
        Write data into file.

        Returns:
            dict: compressor file information. Keys `'name'`, `'size'`.
        """
        file_output = '%s%s' % (
                        currentCompressorFile.name,
                        currentCompressorFile.extention
                    )

        with open(file_output, 'wb') as file:
            file.write(currentCompressorFile.bytes_data.getvalue())

        return {
                'name': file_output,
                'size': '%.2f %s' % (
                                currentCompressorFile.size,
                                currentCompressorFile.unit.upper()
                            )
            }
