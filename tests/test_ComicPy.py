# -*- coding: utf-8 -*-
"""
Tests ComicPy
"""

from test_Base import BaseTestCase

from comicpy.comicpy import ComicPy
from comicpy.exceptionsClasses import (
    UnitFileSizeInvalid,
    ErrorFileBase,
    FilePasswordProtected,
    InvalidFile,
    EmptyFile,
    FileExtentionNotMatch,
    DirectoryPathNotExists,
    DirectoryFilterEmptyFiles,
    DirectoryEmptyFilesValid
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
        currentFile = self.buid_CurrentFile(
                                filename=filename,
                                raw_data=data,
                                return_valid=True
                            )
        is_valid = self.comicpy_init.check_file(currentFile=currentFile)
        self.assertEqual(is_valid, True)

    def test_comicpy_check_filenotmatch(self):
        filename = 'empty.pdf'
        data = self.data[filename]
        currentFile = self.buid_CurrentFile(
                                filename=filename,
                                raw_data=data,
                                return_valid=False,
                                extention='pdf'
                            )
        with self.assertRaises(FileExtentionNotMatch):
            self.comicpy_init.check_file(currentFile=currentFile)

    def test_comicpy_check_file_invalid(self):
        filename = 'empty.pdf'
        data = self.data[filename]
        currentFile = self.buid_CurrentFile(
                                filename=filename,
                                raw_data=data,
                                return_valid=False,
                                extention='xx'
                            )
        with self.assertRaises(InvalidFile):
            self.comicpy_init.check_file(currentFile=currentFile)

    def test_comicpy_check_compressor(self):
        with self.assertRaises(ValueError):
            self.comicpy_init.raiser_error_compressor(compressor_str='xx')

    def test_comicpy_check_protectedFileZipNoPass(self):
        filename = 'protected_image_dir_2.zip'
        data = self.data[filename]
        currentFile = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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

        currentFile1 = self.buid_CurrentFile(
                                filename=filename1,
                                raw_data=data1
                            )
        currentFile2 = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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
        currentFile = self.buid_CurrentFile(
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
        data = self.data[filename2]
        currentFile = self.buid_CurrentFile(
                                filename=filename2,
                                raw_data=data
                            )
        compressFileData = self.comicpy_init.pdfphandler.process_pdf(
                                currentFilePDF=currentFile,
                                compressor='rar',
                                resizeImage='preserve'
                            )
        compressedCurrentFileIO = self.comicpy_init.to_compressor(
                filename=filename2,
                listCompressorData=compressFileData,
                compressor='rar',
                join_files=False,
            )

        results = [
            len(compressedCurrentFileIO) == 1,
            isinstance(compressedCurrentFileIO[0], CurrentFile),
            compressedCurrentFileIO[0].extention == '.cbr'
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_rar_wo_pass_w_pass(self):
        fileWpass = 'protected_image_dir_2.rar'
        fileWOpass = 'image_dir_1.rar'

        dataWpass = self.data[fileWpass]
        currentFileWpass = self.buid_CurrentFile(
                                filename=fileWpass,
                                raw_data=dataWpass
                            )

        dataWOpass = self.data[fileWOpass]
        currentFileWOpass = self.buid_CurrentFile(
                                filename=fileWOpass,
                                raw_data=dataWOpass
                            )

        compressorWpass = self.comicpy_init.rarhandler.extract_content(
                                    currentFileRar=currentFileWpass,
                                    password='password',
                                    resizeImage='preserve'
                                )

        compressorWOpass = self.comicpy_init.rarhandler.extract_content(
                                    currentFileRar=currentFileWOpass,
                                    password='password',
                                    resizeImage='preserve'
                                )

        currentFileCompressorWPass = self.comicpy_init.to_compressor(
                            filename=compressorWpass.filename,
                            listCompressorData=[compressorWpass],
                            compressor='rar',
                            join_files=False
                        )

        currentFileCompressorWOPass = self.comicpy_init.to_compressor(
                            filename=compressorWpass.filename,
                            listCompressorData=[compressorWpass],
                            compressor='rar',
                            join_files=False
                        )

        results = [
            len(compressorWpass.list_data) == 2,
            isinstance(compressorWpass, CompressorFileData),
            isinstance(currentFileCompressorWPass[0], CurrentFile),
            len(compressorWOpass.list_data) == 1,
            isinstance(compressorWOpass, CompressorFileData),
            isinstance(currentFileCompressorWOPass[0], CurrentFile)
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_rar_no_images(self):
        filename = 'no_image.rar'

        data = self.data[filename]
        currentFile = self.buid_CurrentFile(
                                filename=filename,
                                raw_data=data
                            )

        compressorFile = self.comicpy_init.rarhandler.extract_content(
                                    currentFileRar=currentFile,
                                    password='password',
                                    resizeImage='preserve'
                                )
        self.assertEqual(compressorFile, None)

    def test_comicpy_process_zip_wo_pass_w_pass(self):
        fileWpass = 'protected_image_dir_2.zip'
        fileWOpass = 'image_dir_1.zip'

        dataWpass = self.data[fileWpass]
        currentFileWpass = self.buid_CurrentFile(
                                filename=fileWpass,
                                raw_data=dataWpass
                            )

        dataWOpass = self.data[fileWOpass]
        currentFileWOpass = self.buid_CurrentFile(
                                filename=fileWOpass,
                                raw_data=dataWOpass
                            )

        compressorWpass = self.comicpy_init.ziphandler.extract_content(
                                    currentFileZip=currentFileWpass,
                                    password='password',
                                    resizeImage='preserve'
                                )

        compressorWOpass = self.comicpy_init.ziphandler.extract_content(
                                    currentFileZip=currentFileWOpass,
                                    password='password',
                                    resizeImage='preserve'
                                )

        currentFileCompressorWPass = self.comicpy_init.to_compressor(
                            filename=compressorWpass.filename,
                            listCompressorData=[compressorWpass],
                            compressor='zip',
                            join_files=False
                        )

        currentFileCompressorWOPass = self.comicpy_init.to_compressor(
                            filename=compressorWpass.filename,
                            listCompressorData=[compressorWOpass],
                            compressor='zip',
                            join_files=False
                        )

        results = [
            isinstance(compressorWpass, CompressorFileData),
            isinstance(currentFileCompressorWPass[0], CurrentFile),
            isinstance(compressorWOpass, CompressorFileData),
            isinstance(currentFileCompressorWOPass[0], CurrentFile)
        ]
        self.assertEqual(all(results), True)

    def test_comicpy_process_zip_no_images(self):
        filename = 'no_image.zip'

        data = self.data[filename]
        currentFile = self.buid_CurrentFile(
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
                    extention_filter='pdf',
                    filename=None,
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_process_dir_RAR(self):
        list_Currentfiles = self.comicpy_init.process_dir(
                    directory_path=self.rars_dir,
                    extention_filter='rar',
                    filename=None,
                    password=None,
                    compressor='rar',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertEqual(isinstance(list_Currentfiles, list), True)

    def test_comicpy_process_dir_RAR_protected(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.rars_protected,
                    extention_filter='rar',
                    filename='RarProtected',
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
                    extention_filter='rar',
                    filename='RarProtected',
                    password='none',
                    compressor='rar',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertEqual(results, None)

    def test_comicpy_process_dir_ZIP(self):
        result = self.comicpy_init.process_dir(
                    directory_path=self.zips_dir,
                    extention_filter='zip',
                    filename='ZIPS',
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(result, None)

    def test_comicpy_process_dir_ZIP_protected(self):
        result = self.comicpy_init.process_dir(
                    directory_path=self.zips_protected,
                    extention_filter='zip',
                    filename='ZIPS',
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
                    extention_filter='zip',
                    filename='ZipProtected',
                    password='none',
                    compressor='zip',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertEqual(results, None)

    def test_comicpy_process_dir_PDF_JOIN(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.pdfs_dir,
                    extention_filter='pdf',
                    filename=None,
                    password=None,
                    compressor='zip',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_process_dir_ZIP_JOIN(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.zips_dir,
                    extention_filter='zip',
                    filename='ZIPS',
                    password=None,
                    compressor='zip',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_process_dir_RAR_JOIN(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.rars_dir,
                    extention_filter='rar',
                    filename=None,
                    password=None,
                    compressor='rar',
                    join=True,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_dir_cbr(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.cbr_cbz_dir,
                    extention_filter='rar',
                    filename=None,
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
                    extention_filter='zip',
                    filename=None,
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_dir_no_images_zip_rar(self):
        dirname = self.no_image_zip_rar
        noImagesZIP = self.comicpy_init.process_dir(
                    directory_path=dirname,
                    extention_filter='zip',
                    filename=None,
                    password='password',
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        noImagesRAR = self.comicpy_init.process_dir(
                    directory_path=dirname,
                    extention_filter='rar',
                    filename=None,
                    password='password',
                    compressor='rar',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )

        results = [
            noImagesZIP is None,
            noImagesRAR is None
        ]

        self.assertEqual(all(results), True)

    def test_comicpy_dir_images(self):
        dirname = self.images_dir
        results = self.comicpy_init.process_dir(
                    directory_path=dirname,
                    extention_filter='images',
                    filename='Images_Dir_',
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

#
# Write TESTS

    def test_comicpy_to_write_ZIP(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.zips_dir,
                    extention_filter='zip',
                    filename='ZIPS__',
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_to_write_RAR(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.rars_dir,
                    extention_filter='rar',
                    filename=None,
                    password=None,
                    compressor='rar',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_to_write_CBZ(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.cbr_cbz_dir,
                    extention_filter='zip',
                    filename='CBZ__',
                    password=None,
                    compressor='zip',
                    join=False,
                    resize='preserve',
                    dest=self.temp_dir
            )
        self.assertNotEqual(results, None)

    def test_comicpy_to_write_CBR(self):
        results = self.comicpy_init.process_dir(
                    directory_path=self.cbr_cbz_dir,
                    extention_filter='rar',
                    filename='CBR__',
                    password=None,
                    compressor='rar',
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
