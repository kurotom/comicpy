# -*- coding: utf-8 -*-
"""
Checks files looking theris file signatures.
"""


from comicpy.filesigns import hexSignsDict

from typing import Union, TypeVar

CurrentFile = TypeVar('CurrentFile')


class CheckFile:
    """
    Class in charge of checking if the given file is valid based on its
    signature and extension.
    """

    def check(
        self,
        currenf_file: CurrentFile,
    ) -> Union[bool, None]:
        """
        Checks if file is valid.

        Args:
            currenf_file: `CurrentFile` instance contains data of file.

        Returns:
            bool: `True` if file is valid, otherwise `False`.

        Raises:
            KeyError: if the file extension is not valid with respect to its
                      signature.
        """
        try:
            extention = currenf_file.extention.replace('.', '')
            if extention == 'cbr':
                extention_file = 'rar'
            elif extention == 'cbz':
                extention_file = 'zip'
            else:
                extention_file = extention
            data = hexSignsDict[extention_file]
        except KeyError:
            return None

        match_bool = False
        list_hexsigns = data['hexsigns']
        byteoffet = data['byteoffet']
        hexsign_file = self.to_hexsign(raw_data=currenf_file.chunk_bytes)

        string_hexsign_file = ' '.join(hexsign_file)

        for hexsign in list_hexsigns:
            tuple_hexsigns = tuple(zip(hexsign.split(' '), hexsign_file))
            result_bools = [i[0] == i[1] for i in tuple_hexsigns]
            falses = result_bools.count(False)
            # print(string_hexsign_file, falses)
            if 0 <= falses < 2:
                # print(hexsign, string_hexsign_file)
                match_bool = True
                break
            elif falses == 1:
                print('---> ', hexsign, '--', string_hexsign_file)
        return match_bool

    def to_hexsign(
        self,
        raw_data: bytes
    ) -> list:
        """
        Builds the hexadecimal sign from a byte chunk of the file.

        Args:
            raw_data: bytes of file content.

        Returns:
            list: list of strings with the hexadecimal sign.
        """
        hexsign = ''
        hex_signs_list = []
        for i_byte in raw_data:
            ahex = hex(i_byte)[2:]
            if ahex.isnumeric():
                ahex = '%02d' % int(ahex)
            hexsign += ahex.upper()
        for x in range(0, len(hexsign), 2):
            if x > 12:
                hex_signs_list.append(hexsign[x - 1:])
            else:
                hex_signs_list.append(hexsign[x:x + 2])
        return hex_signs_list
