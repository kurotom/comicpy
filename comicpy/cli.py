# -*- coding: utf-8 -*-
"""
CLI comicpy
"""

import argparse
import sys

from comicpy.comicpy import ComicPy
from comicpy.utils import Paths


def pdf(
    comicInstance: ComicPy,
    filename: str,
    compressor: str,
    dest: str,
    check: bool,
    resize: str = 'preserve',
    motor: str = 'pypdf'
) -> None:
    """
    Function for PDF file.
    """
    data = comicInstance.process_pdf(
                    filename=filename,
                    compressor=compressor,
                    resize=resize,
                    motor=motor,
                    dest=dest
                )
    if data is not None and check is True:
        for item in data:
            comicInstance.check_integrity(
                    filename=item['name'],
                    show=True
                )


def rar(
    comicInstance: ComicPy,
    filename: str,
    dest: str,
    check: bool,
    password: str,
    resize: str = 'preserve'
) -> None:
    """
    Function for RAR file.
    """
    data = comicInstance.process_rar(
                    filename=filename,
                    password=password,
                    resize=resize,
                    dest=dest
                )
    if data is not None and check is True:
        for item in data:
            comicInstance.check_integrity(
                    filename=item['name'],
                    show=True
                )


def zip(
    comicInstance: ComicPy,
    filename: str,
    dest: str,
    check: bool,
    password: str,
    resize: str = 'preserve'
) -> None:
    """
    Function for ZIP file.
    """
    data = comicInstance.process_zip(
                    filename=filename,
                    password=password,
                    resize=resize,
                    dest=dest
                )
    if data is not None and check is True:
        for item in data:
            comicInstance.check_integrity(
                        filename=item['name'],
                        show=True
                    )


def dir(
    comicInstance: ComicPy,
    directory_path: str,
    extention_filter: str,
    dest: str,
    filename: str = None,
    password: str = None,
    compressor: str = 'zip',
    join: bool = False,
    check: bool = False,
    resize: str = 'preserve',
    motor: str = 'pypdf'
) -> None:
    """
    Function for directories.
    """
    data = comicInstance.process_dir(
                    filename=filename,
                    directory_path=directory_path,
                    extention_filter=extention_filter,
                    compressor=compressor,
                    join=join,
                    password=password,
                    resize=resize,
                    motor=motor,
                    dest=dest
                )
    # print('--> ', data)
    if data is not None and check is True:
        for item in data:
            comicInstance.check_integrity(
                        filename=item['name'],
                        show=True
                    )


def CliComicPy() -> None:
    """
    Main CLI function.
    """
    paths = Paths()

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
            choices=['pdf', 'rar', 'zip', 'cbr', 'cbz', 'images'],
            default='zip',
            help='Filter files on directory.'
        )
    main_parser.add_argument(
            '--motorPDF',
            choices=['pypdf', 'pymupdf'],
            default='pypdf',
            help='PDF library to use.'
        )
    main_parser.add_argument(
            '-c',
            '--compressor',
            default='zip',
            choices=['rar', 'zip'],
            help='Type of compressor to use.',
        )
    main_parser.add_argument(
            '-d',
            '--dest',
            default='.',
            help='Path to save output files. Default is "."',
        )
    ##########################################
    # TODO: delete?
    main_parser.add_argument(
            '-o',
            '--output',
            help='Prefix of output file.',
        )
    ##########################################
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
            help='Join or not the files found in the directory. Default is \
            "False".',
        )
    main_parser.add_argument(
            '-u',
            '--unit',
            choices=['b', 'kb', 'mb', 'gb'],
            default='mb',
            help='Unit of measure of data size. Default is "mb"',
        )
    main_parser.add_argument(
            '--password',
            help='Password of file protected.'
        )
    main_parser.add_argument(
            '--resize',
            choices=['preserve', 'small', 'medium', 'large'],
            default='preserve',
            help='Resize images.'
        )
    main_parser.add_argument(
            '--path_exec',
            default=None,
            help='Path of RAR executable.'
        )
    main_parser.add_argument(
            '--progress',
            default=False,
            action='store_true',
            help='Shows file in progress.'
        )

    args = main_parser.parse_args()
    typeFile = args.type
    pathFile = args.path
    filterFile = args.filter
    compressorFile = args.compressor
    destFile = args.dest
    outputFile = args.output
    checkFile = args.check
    unitFile = args.unit
    joinFile = args.join
    password = args.password
    resizeImage = args.resize
    path_exec = args.path_exec
    progress = args.progress
    motorPDF = args.motorPDF

    # Instance
    comic = ComicPy(
                unit=unitFile,
                exec_path_rar=path_exec,
                show_progress=progress
            )
    try:
        # FILE
        if typeFile == 'f':
            name_, extention_ = paths.splitext(pathFile)
            if extention_.lower() == '.pdf':
                pdf(
                    comicInstance=comic,
                    filename=pathFile,
                    compressor=compressorFile,
                    dest=destFile,
                    check=checkFile,
                    resize=resizeImage,
                    motor=motorPDF
                )
            if extention_.lower() == '.rar' or extention_.lower() == '.cbr':
                rar(
                    comicInstance=comic,
                    filename=pathFile,
                    dest=destFile,
                    check=checkFile,
                    password=password,
                    resize=resizeImage
                )

            if extention_.lower() == '.zip' or extention_.lower() == '.cbz':
                zip(
                    comicInstance=comic,
                    filename=pathFile,
                    dest=destFile,
                    check=checkFile,
                    password=password,
                    resize=resizeImage
                )

        # DIRECOTRY
        elif typeFile == 'd':

            dir(
                comicInstance=comic,
                directory_path=pathFile,
                extention_filter=filterFile,
                dest=destFile,
                filename=pathFile,
                password=password,
                compressor=compressorFile,
                join=joinFile,
                check=checkFile,
                resize=resizeImage,
                motor=motorPDF
            )

    except KeyboardInterrupt:
        print('Interrumped by user.')
        sys.exit(1)


if __name__ == '__main__':
    CliComicPy()
