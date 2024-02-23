# -*- coding: utf-8 -*-
"""
CLI comicpy
"""

import argparse
import os

from comicpy.comicpy import ComicPy


def pdf(
    comicInstance: ComicPy,
    filename: str,
    compressor: str,
    dest: str,
    check: bool,
) -> None:
    data = comicInstance.process_pdf(
                    filename=filename,
                    compressor=compressor
                )
    metaFileCompress = comicInstance.write_cbz(
                    currentFileZip=data,
                    path=dest
                )
    if check:
        for item in metaFileCompress:
            comicInstance.check_integrity(
                    filename=item['name'],
                    show=True
                )


def rar(
    comicInstance: ComicPy,
    filename: str,
    dest: str,
    check: bool,
) -> None:
    # RAR
    print(filename, dest, check)
    data = comicInstance.process_rar(filename=filename)
    metaFileCompress = comicInstance.write_cbr(
                                currentFileRar=data,
                                path=dest
                            )
    if check:
        for item in metaFileCompress:
            comicInstance.check_integrity(
                    filename=item['name'],
                    show=True
                )


def zip(
    comicInstance: ComicPy,
    filename: str,
    dest: str,
    check: bool,
) -> None:
    # ZIP
    data = comicInstance.process_zip(filename=filename)
    metaFileCompress = comicInstance.write_cbz(
                                currentFileZip=data,
                                path=dest
                            )
    if check:
        for item in metaFileCompress:
            comicInstance.check_integrity(
                        filename=item['name'],
                        show=True
                    )


def CliComicPy() -> None:
    """
    Main CLI function.
    """

    main_parser = argparse.ArgumentParser(
                prog='ComicPy',
                description='Convert PDF, RAR, ZIP files to CBR or CBZ.',
                epilog='Allows you to manage individual files or directories.'
            )

    main_parser.add_argument(
            '--type',
            choices=['f', 'd'],
            required=True,
            help='File or Directory.'
        )
    main_parser.add_argument(
            '-p',
            '--path',
            required=True,
            help='Path of file or directory.'
        )
    main_parser.add_argument(
            '--filter',
            choices=['pdf', 'rar', 'zip', 'cbr', 'cbz'],
            default='zip',
            help='Filter files on directory.'
        )
    main_parser.add_argument(
            '-c',
            '--compress',
            default='zip',
            choices=['rar', 'zip'],
            help='Type of compress to use.',
        )
    main_parser.add_argument(
            '-d',
            '--dest',
            default='.',
            help='Path to save output files. Default is "."',
        )
    main_parser.add_argument(
            '-o',
            '--output',
            default='Converted_',
            help='Prefix of output file.',
        )
    main_parser.add_argument(
            '--check',
            action='store_true',
            default=False,
            help='Check the CBR or CBZ files created.',
        )
    main_parser.add_argument(
            '--join',
            default=False,
            action='store_true',
            help='Join or does not files thath are in the directory.\
            Default is "False".',
        )
    main_parser.add_argument(
            '-u',
            '--unit',
            choices=['b', 'kb', 'mb', 'gb'],
            default='mb',
            help='Unit of measure of data size. Default is "mb"',
        )

    args = main_parser.parse_args()
    typeFile = args.type
    pathFile = args.path
    filterFile = args.filter
    compressFile = args.compress
    destFile = args.dest
    outputFile = args.output
    checkFile = args.check
    unitFile = args.unit
    joinFile = args.join

    # Instance
    comic = ComicPy(unit=unitFile)

    if typeFile == 'f':
        name_, extention_ = os.path.splitext(pathFile)
        # FILE
        if extention_.lower() == '.pdf':
            pdf(
                comicInstance=comic,
                filename=pathFile,
                compressor=compressFile,
                dest=destFile,
                check=checkFile
            )
        if extention_.lower() == '.rar':
            rar(
                comicInstance=comic,
                filename=pathFile,
                dest=destFile,
                check=checkFile,
            )

        if extention_.lower() == '.zip':
            zip(
                comicInstance=comic,
                filename=pathFile,
                dest=destFile,
                check=checkFile
            )

    elif typeFile == 'd':
        # DIRECOTRY
        dir_name = os.path.basename(pathFile)
        name = '%s%s' % (outputFile, dir_name)
        data = comic.process_dir(
                        filename=name,
                        directory_path=pathFile,
                        extention_filter=filterFile,
                        compressor=compressFile,
                        join=joinFile
                    )
        if compressFile == 'rar':
            metaFileCompress = comic.write_cbr(
                                    currentFileRar=data,
                                    path=destFile
                                )
        elif compressFile == 'zip':
            metaFileCompress = comic.write_cbz(
                                    currentFileZip=data,
                                    path=destFile
                                )
        if checkFile:
            for item in metaFileCompress:
                comic.check_integrity(filename=item['name'], show=True)


if __name__ == '__main__':
    CliComicPy()
