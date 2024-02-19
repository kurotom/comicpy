# -*- coding: utf-8 -*-
"""
"""


from comicpy.filesigns import hexSignsDict

import io

from typing import Union, TypeVar

CurrentFileClass = TypeVar('CurrentFileClass')


class CheckFile:

    def check(
        self,
        currenf_file: CurrentFileClass,
    ) -> Union[bool, None]:
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

        match = False
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
                match = True
                break
            elif falses == 1:
                print('---> ', hexsign, '--', string_hexsign_file)
        return match

    def to_hexsign(
        self,
        raw_data: bytes
    ) -> list:
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
