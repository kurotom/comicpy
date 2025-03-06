# -*- coding: utf-8 -*-
"""
CLI comicpy
"""

import argparse
import sys

from comicpy.comicpycontroller import ComicPy
from comicpy.utils import Paths
from comicpy.version import VERSION


def pdf(
    comicInstance: ComicPy,
    filename: str,
    compressor: str,
    # dest: str,
    check: bool,
    resize: str = 'preserve',
    motor: str = 'pymupdf'
) -> None:
    """
    Function for PDF file.
    """
    data = comicInstance.process_pdf(
                    filename=filename,
                    compressor=compressor,
                    resize=resize,
                    # motor=motor
                    # dest=dest
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
    # dest: str,
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
                    # dest=dest
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
    # dest: str,
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
                    # dest=dest
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
    extension_filter: str,
    # dest: str,
    filename: str = None,
    password: str = None,
    compressor: str = 'zip',
    join: bool = False,
    check: bool = False,
    resize: str = 'preserve',
    motor: str = 'pymupdf'
) -> None:
    """
    Function for directories.
    """
    data = comicInstance.process_dir(
                    directory_path=directory_path,
                    extension_filter=extension_filter,
                    compressor=compressor,
                    join=join,
                    password=password,
                    resize=resize
                    # motor=motor
                    # dest=dest
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
    main_parser = argparse.ArgumentParser(
                prog='ComicPy',
                description='Convert PDF, RAR, ZIP files to CBR or CBZ.',
                epilog='Allows you to manage individual files or directories.'
            )

    main_parser.add_argument(
            '--type',
            choices=['f', 'd'],
            help='File or Directory.'
        )
    main_parser.add_argument(
            '-p',
            '--path',
            help='Path of file or directory.'
        )
    main_parser.add_argument(
            '--filter',
            choices=['pdf', 'rar', 'zip', 'cbr', 'cbz', 'images'],
            default='zip',
            help='Filter files on directory.'
        )

    main_parser.add_argument(
            '-c',
            '--compressor',
            default='zip',
            choices=['rar', 'zip'],
            help='Type of compressor to use.',
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

    main_parser.add_argument(
            '--version',
            default=False,
            action='store_true',
            help='Shows version of ComicPy.'
        )

    args = main_parser.parse_args()
    typeFile = args.type
    pathFile = args.path
    filterFile = args.filter
    compressorFile = args.compressor
    checkFile = args.check
    unitFile = args.unit
    joinFile = args.join
    password = args.password
    resizeImage = args.resize
    path_exec = args.path_exec
    progress = args.progress
    version = args.version

    # Instance
    comic = ComicPy(
                unit=unitFile,
                exec_path_rar=path_exec,
                show_progress=progress
            )
    try:
        if version:
            print(f"\ncomicpy version: {VERSION}\n")
        # FILE
        elif typeFile == 'f':

            if pathFile is None:
                print("\nNeeds '--path' parameter of the file.\n")
                return

            name_, extension_ = Paths.splitext(pathFile)
            if extension_.lower() == '.pdf':
                pdf(
                    comicInstance=comic,
                    filename=pathFile,
                    compressor=compressorFile,
                    check=checkFile,
                    resize=resizeImage
                )
            if extension_.lower() == '.rar' or extension_.lower() == '.cbr':
                rar(
                    comicInstance=comic,
                    filename=pathFile,
                    check=checkFile,
                    password=password,
                    resize=resizeImage
                )

            if extension_.lower() == '.zip' or extension_.lower() == '.cbz':
                zip(
                    comicInstance=comic,
                    filename=pathFile,
                    check=checkFile,
                    password=password,
                    resize=resizeImage
                )

        # DIRECTORY
        elif typeFile == 'd':
            if pathFile is None:
                print("\nNeeds '--path' parameter of the file.\n")
                return

            dir(
                comicInstance=comic,
                directory_path=pathFile,
                extension_filter=filterFile,
                password=password,
                compressor=compressorFile,
                join=joinFile,
                check=checkFile,
                resize=resizeImage
            )

    except KeyboardInterrupt:
        print('Interrumped by user.')
        sys.exit(1)


if __name__ == '__main__':
    CliComicPy()
