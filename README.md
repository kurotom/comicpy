# comicpy

Tool to create CBR or CBZ files.

Extracts images from PDF, ZIP, CBR files, generating comic files respecting their original order.


> [!Important]
>> The original files are not altered.
>


## Features

* Convert `PDF` file to `CBR` or `CBZ` files (by default).
* Convert `RAR` files to `CBR` files.
* Convert `ZIP` files to `CBZ` files.
* Scan in given directory and filter `PDF`, `ZIP`, `RAR` files depending on the given extension, convert them into `CBR` or `CBZ` files, generating individual files or consolidated into one.
* Scan in the given directory and filter `CBR`, `CBZ` files allowing to merge them all into one.
* Extract `CBR` or `CBZ` files from `RAR` or `ZIP` archives.
* Support for password protected `RAR` or `ZIP` archives.
* Convert image directories (*jpeg*, *png*, *jpg*) to `CBR` or `CBZ` files.


> [!Important]
>> 1. For full operation of `comicpy` when using RAR files, you must have available the `rar` command, download and install it from the official site, [**rarlab - rar/unrar command**](https://www.rarlab.com/download.htm).
>
>> 2. Some PDF files *contain multiple images on the same page*, which may be *repeated* within the *same file*; converting the PDF file <u>will remove all duplicate images</u>. <u>This is due to the original construction and layout of the source PDF file</u>. Therefore, as a result, there may be fewer or more pages compared to the original PDF file, this does *not necessarily indicate that the work of this tool (**comicpy**) is flawed or faulty*.
>
>> In continuous development of `comicpy`, any problem, suggestion, doubt, leave it in [*Issues*](https://github.com/kurotom/comicpy/issues) of the repository.
>


# Installation

```bash
pip install comicpy
```

# Usage

## CLI - usage

Command help.

```bash
$ comicpy -h
```

### File usage

| Command | Description |
|-|-|
| --type f | File. |
| -p PATH, --path PATH | Path of file. |
| -d DEST, --dest DEST | Path to save output files. Default is "." |
| --motorPDF {pypdf,pymupdf} | PDF library to use. |
| -c {rar,zip}, --compressor {rar,zip} | Type of compressor to use. |
| -o OUTPUT, --output OUTPUT | Prefix of output file. |
| --check | Check the CBR or CBZ files created. |
| -u {b,kb,mb,gb}, --unit {b,kb,mb,gb} | Unit of measure of data size. Default is "mb". |
| --password PASSWORD | Password of file protected. |
| --resize {preserve,small,medium,large} | Resize images. |
| --progress | Shows file in progress. |

```bash
$ comicpy --type f -p file.PDF --check -u kb
$
$ comicpy --type f -p file.rar --check
$
$ comicpy --type f -p file.zip --check --password PASS
$
$ comicpy --type f -p file.rar --check --resize small
```

### Directory usage

| Command | Description |
|-|-|
| --type d | Directory. |
| -p PATH, --path PATH | Path of directory. |
| --filter {pdf,rar,zip,cbr,cbz,images} | Filter files on directory. Default is "zip". |
| --motorPDF {pypdf,pymupdf} | PDF library to use. |
| -c {rar,zip}, --compressor {rar,zip} | Type of compressor to use. Default is "zip".|
| -d DEST, --dest DEST | Path to save output files. Default is ".".
| -o OUTPUT, --output OUTPUT | Prefix of output file. Default is "Converted_". |
| --check | Check the CBR or CBZ files created. |
| --join | Join or does not files thath are in the directory. Default is "False". |
| -u {b,kb,mb,gb}, --unit {b,kb,mb,gb} | Unit of measure of data size. Default is "mb". |
| --password PASSWORD | Password of file protected. |
| --resize {preserve,small,medium,large} | Resize images. |
| --progress | Shows file in progress. |


```bash
$ comicpy --type d -p rars_dir --filter rar -c rar --check --join -o prefix_final_ --password PASS
$ for i in $(ls -d Zip_Dir_*/); do
> comicpy --type d -p "$i" --filter zip -c zip --check -o ${i: 0:-1} --join
> done
$ comicpy --type d -p rars_dir --filter rar -c rar --check --join -o prefix_final_ --password PASS --resize preserve
$ comicpy --type d -p Comic_vol1/ --compress zip --filter images --check --progress --join
```



## Development - usage

> `path='.'` parameter indicates that files will be written by default to the current directory. It can be changed.

## Single PDF, RAR, ZIP file -> CBZ or CBR

```python
>>> from comicpy import ComicPy
>>>
>>> pdf_file = 'file_pdf.PDF'
>>>
>>> comic = ComicPy(unit='mb')
>>>
>>> metaFileCompress = comic.process_pdf(filename=pdf_file, compressor='zip')
>>>
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
>>> metaFileCompress = comic.process_dir(
...             filename='final_CBR_file',
...             directory_path=dir_RAR,
...             extention_filter='rar',
...             compressor='rar',
...             password=None,
...             join=False
...           )
>>> print(metaFileCompress)
[
  {'name': './final_CBR_file/chapter_1.cbr', 'size': '0.02 GB'},
  {'name': './final_CBR_file/chapter_2.cbr', 'size': '0.01 GB'}
]
>>>>
>>> for item in metaFileCompress:
...   comic.check_integrity(
...      filename=item['name'],
...      show=True
...   )
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
>>> metaFileCompress = comic.process_dir(
...                 filename='final_CBR_file',
...                 directory_path=dir_RAR,
...                 extention_filter='rar',
...                 compressor='rar',
...                 password=None,
...                 join=True
...               )
>>> print(metaFileCompress)
[{'name': 'result/final_CBR_file/final_CBR_file.cbr', 'size': '0.05 GB'}]
>>>
>>> for item in metaFileCompress:
...   comic.check_integrity(
...      filename=item['name'],
...      show=True
...   )
...
File is valid?:  "True"
True
>>>
```

### Cloning, preparing the environment and running the tests

Linux environment.

```bash
git clone https://github.com/kurotom/comicpy.git

cd comicpy

poetry shell

poetry install

. run_tests.sh
```
