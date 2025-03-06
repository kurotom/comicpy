# -*- coding: utf-8 -*-
"""
Tests ComicPy
"""

from test_Base import BaseTestCase

from comicpy.comicpycontroller import ComicPy
from comicpy.exceptionsClasses import (
    UnitFileSizeInvalid,
    ErrorFileBase,
    FilePasswordProtected,
    BadPassword,
    InvalidFile,
    EmptyFile,
    ExtensionError,
    FileExtensionNotMatch,
    DirectoryPathNotExists,
    DirectoryFilterEmptyFiles,
    DirectoryEmptyFilesValid,
    InvalidCompressor
)

from comicpy.models import (
    CurrentFile,
    CompressorFileData
)

import os
import shutil


class ComicPyTestCase(BaseTestCase):

    def test_comicpy_invalid_unit(self):
        with self.assertRaises(UnitFileSizeInvalid):
            self.comicpy('XX')

    def test_comicpy_read_file(self):
        file = self.files['empty.pdf']
        obj = self.comicpy_init.read(filename=file)
        self.assertEqual(isinstance(obj, CurrentFile), True)

    def test_comicpy_check_file_valid(self):
        filename = 'empty.pdf'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data,
                                return_valid=True
                            )
        is_valid = self.comicpy_init.check_file(currentFile=currentFile)
        self.assertEqual(is_valid, True)

    def test_comicpy_check_filenotmatch(self):
        filename = 'empty.pdf'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data,
                                return_valid=False,
                                extension='pdf'
                            )
        with self.assertRaises(FileExtensionNotMatch):
            self.comicpy_init.check_file(currentFile=currentFile)

    def test_comicpy_check_file_invalid(self):
        filename = 'empty.pdf'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data,
                                return_valid=False,
                                extension='xx'
                            )
        with self.assertRaises(InvalidFile):
            self.comicpy_init.check_file(currentFile=currentFile)

    def test_comicpy_check_compressor(self):
        with self.assertRaises(InvalidCompressor):
            self.comicpy_init.raiser_error_compressor(compressor_str='xx')

    def test_comicpy_check_protectedFileZipNoPass(self):
        filename = 'protected_image_dir_2.zip'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )

        with self.assertRaises(FilePasswordProtected):
            self.comicpy_init.check_protectedFile(
                handler=self.comicpy_init.ziphandler,
                compressCurrentFile=currentFile,
                password=None
            )

    def test_comicpy_check_protectedFileRarNoPass(self):
        filename = 'protected_image_dir_2.rar'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )
        with self.assertRaises(FilePasswordProtected):
            self.comicpy_init.check_protectedFile(
                handler=self.comicpy_init.rarhandler,
                compressCurrentFile=currentFile,
                password=None
            )

    def test_comicpy_read_file_NoExecRAR(self):
        origin_paths = os.environ['PATH']

        comicpy_inst = self.comicpy()
        os.environ['PATH'] = ''

        filename = 'image_dir_2.rar'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )
        result = comicpy_inst.rarhandler.extract_content(
                                    currentFileRar=currentFile,
                                    password=None,
                                    resizeImage='preserve'
                                )
        os.environ['PATH'] = origin_paths
        self.assertEqual(result, -1)

    def test_comicpy_check_FileZip(self):
        filename = 'image_dir_1.zip'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )
        boolean = self.comicpy_init.check_protectedFile(
            handler=self.comicpy_init.ziphandler,
            compressCurrentFile=currentFile,
            password=None
        )
        self.assertFalse(boolean)

    def test_comicpy_check_FileRar(self):
        filename = 'image_dir_1.rar'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )
        boolean = self.comicpy_init.check_protectedFile(
            handler=self.comicpy_init.rarhandler,
            compressCurrentFile=currentFile,
            password=None
        )
        self.assertFalse(boolean)

    def test_pdfhandler_process_pdf(self):
        filename2 = 'image.pdf'
        data = self.data[filename2]
        currentFile = self.build_CurrentFile(
                                filename=filename2,
                                raw_data=data
                            )
        results = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile,
                                compressor='rar',
                                resizeImage='preserve',
                                motor='pypdf'
                            )
        data = [
            isinstance(results, CompressorFileData),
            len(results.list_data) == 1
        ]
        self.assertEqual(all(data), True)

    def test_pdfhandler_process_pdf_MultiImages_PYPDF(self):
        filename1 = 'comic 1.pdf'
        filename2 = 'comic 2.pdf'

        data1 = self.data[filename1]
        data2 = self.data[filename2]

        currentFile1 = self.build_CurrentFile(
                                filename=filename1,
                                raw_data=data1
                            )
        currentFile2 = self.build_CurrentFile(
                                filename=filename2,
                                raw_data=data2
                            )

        compressFileData1 = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile1,
                                compressor='rar',
                                resizeImage='preserve',
                                motor='pypdf'
                            )
        compressFileData2 = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile2,
                                compressor='zip',
                                resizeImage='preserve',
                                motor='pypdf'
                            )

        results = [
            len(compressFileData1.list_data) == 4,
            compressFileData1.type == 'rar',
            len(compressFileData2.list_data) == 4,
            compressFileData2.type == 'zip',
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_pdf_MultiImageSorted_PYPDF(self):
        filename = 'image_2.pdf'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )
        compressFileData = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile,
                                compressor='rar',
                                resizeImage='preserve',
                                motor='pypdf'
                            )

        results = [
            len(compressFileData.list_data) == 4,
            compressFileData.type == 'rar'
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_pdfMultiImageNotSorted_PYPDF(self):
        # original order must be preserve
        filename = 'comic 1.pdf'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )
        compressFileData = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile,
                                compressor='rar',
                                resizeImage='preserve',
                                motor='pypdf'
                            )

        results = [
            len(compressFileData.list_data) == 4,
            compressFileData.type == 'rar'
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_pdf_empty_images(self):
        filename = 'file.pdf'
        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )
        result = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile,
                                compressor='rar',
                                resizeImage='preserve'
                            )
        self.assertEqual(result, None)

    def test_comicpy_to_compressor(self):
        filename2 = 'image.pdf'
        path = self.FILES[filename2]
        data = self.data[filename2]
        currentFile = self.build_CurrentFile(
                                filename=filename2,
                                raw_data=data
                            )
        compressFileData = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile,
                                compressor='rar',
                                resizeImage='preserve'
                            )

        self.comicpy_init.get_base_converted_path(
                origin=path,
                dest=self.temp_dir,
                type='f'
            )

        self.comicpy_init.get_cbz_cbr_name(
                filename=path,
                compressor='rar'
            )

        metadataFile = self.comicpy_init.to_compressor(
                filename=self.comicpy_init.FILE_CBR_CBZ_,
                listCompressorData=compressFileData.list_data,
                compressor='rar',
                join_files=False,
                basedir=self.comicpy_init.BASE_DIR_,
                dest=self.comicpy_init.CONVERTED_COMICPY_PATH_,
            )

        is_valid = self.comicpy_init.check_integrity(
                                filename=metadataFile[0]['name'],
                                show=False
                            )

        results = [
            len(metadataFile) == 1,
            is_valid is True
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_rar_w_pass(self):
        fileWpass = 'protected_image_dir_2.rar'

        dataWpass = self.data[fileWpass]
        currentFileWpass = self.build_CurrentFile(
                                filename=fileWpass,
                                raw_data=dataWpass
                            )

        compressorWpass = self.comicpy_init.rarhandler.extract_content(
                                    currentFileRar=currentFileWpass,
                                    password='password',
                                    resizeImage='preserve'
                                )

        results = [
            compressorWpass is not None,
            compressorWpass.items == 2
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_rar_no_images(self):
        filename = 'no_image.rar'

        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )

        compressorFile = self.comicpy_init.rarhandler.extract_content(
                                    currentFileRar=currentFile,
                                    password='password',
                                    resizeImage='preserve'
                                )
        self.assertEqual(compressorFile, None)

    def test_comicpy_process_zip_w_pass(self):
        fileWpass = 'protected_image_dir_2.zip'

        dataWpass = self.data[fileWpass]
        currentFileWpass = self.build_CurrentFile(
                                filename=fileWpass,
                                raw_data=dataWpass
                            )

        compressorWpass = self.comicpy_init.ziphandler.extract_content(
                                    currentFileZip=currentFileWpass,
                                    password='password',
                                    resizeImage='preserve'
                                )

        results = [
            compressorWpass is not None,
            compressorWpass.items == 2
        ]

        self.assertEqual(all(results), True)

    def test_comicpy_process_zip_no_images(self):
        filename = 'no_image.zip'

        data = self.data[filename]
        currentFile = self.build_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )

        compressorFile = self.comicpy_init.ziphandler.extract_content(
                                    currentFileZip=currentFile,
                                    password='password',
                                    resizeImage='preserve'
                                )
        self.assertEqual(compressorFile, None)

    def test_comicpy_process_dir_PDF(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.pdfs_dir,
                    extension_filter='pdf',
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_process_dir_RAR(self):
        list_Currentfiles = self.comicpy_init.process_dir(
                    directory_path=self.rars_dir,
                    extension_filter='rar',
                    password=None,
                    compressor='rar',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertEqual(isinstance(list_Currentfiles, list), True)

    def test_comicpy_process_dir_RAR_protected(self):
        print(self.rars_protected)
        results = self.comicpy_init.process_dir(
                    directory_path=self.rars_protected,
                    extension_filter='rar',
                    password='password',
                    compressor='rar',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )

        is_valid = self.comicpy_init.check_integrity(
                                    filename=results[0]['name'],
                                    show=False
                                )
        data_results = [
            is_valid is True,
            results is not None
        ]
        self.assertEqual(all(data_results), True)

    def test_comicpy_process_dir_RAR_protected_wrong_pass(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.rars_protected,
                    extension_filter='rar',
                    password='none',
                    compressor='rar',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertEqual(results, [])

    def test_comicpy_process_dir_ZIP(self):
        result = self.comicpy_init.process_dir(
                    directory_path=self.zips_dir,
                    extension_filter='zip',
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        results = [
            isinstance(result, list),
            len(result) == 2
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_dir_ZIP_protected(self):
        result = self.comicpy_init.process_dir(
                    directory_path=self.zips_protected,
                    extension_filter='zip',
                    password='password',
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(result, None)

    def test_comicpy_process_dir_ZIP_protected_wrong_pass(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.zips_protected,
                    extension_filter='zip',
                    password='none',
                    compressor='zip',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertEqual(results, [])

    def test_comicpy_process_dir_PDF_JOIN(self):
        result = self.comicpy_init.process_dir(
                    directory_path=self.pdfs_dir,
                    extension_filter='pdf',
                    password=None,
                    compressor='zip',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        results = [
            isinstance(result, list),
            len(result) == 1
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_dir_ZIP_JOIN(self):
        result = self.comicpy_init.process_dir(
                    directory_path=self.zips_dir,
                    extension_filter='zip',
                    password=None,
                    compressor='zip',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        results = [
            isinstance(result, list),
            len(result) == 1
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_dir_RAR_JOIN(self):
        result = self.comicpy_init.process_dir(
                    directory_path=self.rars_dir,
                    extension_filter='rar',
                    password=None,
                    compressor='rar',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        results = [
            isinstance(result, list),
            len(result) == 1
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_dir_cbr(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.cbr_cbz_dir,
                    extension_filter='rar',
                    password=None,
                    compressor='rar',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_dir_cbz(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.cbr_cbz_dir,
                    extension_filter='zip',
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_dir_no_images_zip_rar(self):
        dirname = self.no_image_zip_rar
        result = self.comicpy_init.process_dir(
                        directory_path=dirname,
                        extension_filter='images',
                        password='password',
                        compressor='zip',
                        join=False,
                        resize='preserve',
                        dest=self.temp_dir
                    )
        self.assertEqual(result, [])

    def test_comicpy_dir_images(self):
        dirname = self.images_dir
        results = self.comicpy_init.process_dir(
                    directory_path=dirname,
                    extension_filter='images',
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    @classmethod
    def tearDownClass(cls):
        path = os.path.join(
                    BaseTestCase.TESTS_DIR,
                    BaseTestCase.TEMP_DIR
                )
        shutil.rmtree(path)
