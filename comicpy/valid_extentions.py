# -*- coding: utf-8 -*-
"""
Extentions valid for program.
"""

pdfFileExtention = {
    'PDF': '.pdf'
}

comicFilesExtentions = {
    'CBR': '.cbr',
    'CBZ': '.cbz'
}

compressorsExtentions = {
    'ZIP': '.zip',
    'RAR': '.rar'
}

imagesExtentions = {
    'JPEG': '.jpeg',
    'PNG': '.png',
    'JPG': '.jpg'
}


validExtentionsList = [
                ext.replace('.', '')
                for ext in (
                            list(pdfFileExtention.values()) +
                            list(comicFilesExtentions.values()) +
                            list(compressorsExtentions.values())
                        )
            ]
