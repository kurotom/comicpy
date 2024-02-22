# comicpy

Tool to create CBR or CBZ files.

Extracts images from PDF, ZIP, CBR files, generating comic files respecting their original order.


> The original files are not altered.

## Features

* Convert `PDF` file to `CBR` or `CBZ` files (by default).
* Convert `RAR` files to `CBR` files.
* Convert `ZIP` files to `CBZ` files.
* Scan in given directory and filter `PDF`, `ZIP`, `RAR` files depending on the given extension, convert them into `CBR` or `CBZ` files, generating individual files or consolidated into one.
* Scan in the given directory and filter `CBR`, `CBZ` files allowing to merge them all into one.


# Installation

```
pip install comicpy
```


# Usage

> `path` parameter of `ComicPy.write_cbr(path='.')`, indicates that files will be written by default to the current directory. It can be changed.

## Single PDF, RAR, ZIP file -> CBZ or CBR

```python
>>> from comicpy import ComicPy
>>>
>>> pdf_file = 'file_pdf.PDF'
>>>
>>> comic = ComicPy(unit='mb')
>>>
>>> data = comic.process_pdf(filename=pdf_file, compressor='zip')
>>>
>>> metaFileCompress = comic.write_cbz(currentFileZip=data)
>>> print(metaFileCompress)
[{'name': './file_pdf/file_pdf.cbz', 'size': '76.63 MB'}]
>>>
>>> comic.check_integrity(filename=metaFileCompress[0]['name'])
File is valid?:  "True"
True
>>>
>>> comic.check_integrity(filename=metaFileCompress[0]['name'], show=False)
True
>>>
```

## Directory with PDFs, RARs, ZIPs files -> CBZ or CBR

> The `join` parameter indicates whether all found files are merged or treated as individual files.


* Example, directory with RAR files - `join=False`


```python
>>> from comicpy import ComicPy
>>>
>>> dir_RAR = 'rars'
>>>
>>> comic = ComicPy(unit='GB')
>>>
>>> data = comic.process_dir(
...             filename='final_CBR_file',
...             directory_path=dir_RAR,
...             extention_filter='rar',
...             compressor='rar',
...             join=False
...           )
>>> metaFileCompress = comic.write_cbr(currentFileRar=data)
>>> print(metaFileCompress)
[{'name': './final_CBR_file/chapter_1.cbr', 'size': '0.02 GB'}, {'name': './final_CBR_file/chapter_2.cbr', 'size': '0.01 GB'}, {'name': './final_CBR_file/chapter_3.cbr', 'size': '0.01 GB'}, {'name': './final_CBR_file/chapter_4.cbr', 'size': '0.01 GB'}]
>>>>
>>> for item in metaFileCompress:
...   comic.check_integrity(filename=item['name'], show=True)
...
File is valid?:  "True"
True
File is valid?:  "True"
True
File is valid?:  "True"
True
File is valid?:  "True"
True
>>>
```


* Example, directory with RAR files - `join=True`

```python
>>> from comicpy import ComicPy
>>>
>>> dir_RAR = 'rars'
>>>
>>> comic = ComicPy(unit='GB')
>>>
>>> data = comic.process_dir(
...                 filename='final_CBR_file',
...                 directory_path=dir_RAR,
...                 extention_filter='rar',
...                 compressor='rar',
...                 join=True
...               )
>>> metaFileCompress = comic.write_cbr(
...                           currentFileRar=data,
...                           path='result'
...                         )
>>> print(metaFileCompress)
[{'name': 'result/final_CBR_file/final_CBR_file.cbr', 'size': '0.05 GB'}]
>>>
>>> for item in metaFileCompress:
...   comic.check_integrity(filename=item['name'], show=True)
...
File is valid?:  "True"
True
>>>
```
