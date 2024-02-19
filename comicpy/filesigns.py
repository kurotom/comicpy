# -*- coding: utf-8 -*-
"""
Signing of files of interest.

The `CBZ` and `CBR` archives have the same file signatures as `ZIP` and `RAR`
respectively.
"""

hexSignsDict = {
    'pdf': {
        'hexsigns': [
            '25 50 44 46',
            '25 50 44 46 2D'
        ],
        'byteoffet': 0
    },
    'zip': {
        'hexsigns': [
            '50 4B 53 70 58',
            '50 4B 03 04 14 00 01 00',
            '63 00 00 00 00 00',
            '50 4B 07 08',
            '50 4B 4C 49 54 45',
            '57 69 6E 5A 69 70',
            '50 4B 03 04',
            '50 4B 05 06'
        ],
        'byteoffet': 0
    },
    'rar': {
        'hexsigns': [
            '52 61 72 21 1A 07 00',    # RAR version 4
            '52 61 72 21 1A 07 01 00'  # RAR version 5
        ],
        'byteoffet': 0
    }

}
