# comicpy

Tool to create CBR or CBZ files.

Extracts images from PDF, ZIP, CBR files, generating comic files respecting their original order.


> The original files are not altered.


# Installation

```
pip install comicpy
```


# Usage

```python
>>> from comicpy import ComicPy
>>>
>>> pdf_file = 'pdf_comic.PDF'
>>>
>>> comic = ComicPy(unit='mb')
>>> data = comic.process_pdf(filename=pdf_file, compressor='zip')
>>>
>>> metaFileCompress = comic.write_cbz(currentFileZip=data)
>>> print(metaFileCompress)
{'name': 'FNAE CAPS 01-04 (TOMO1).cbz', 'size': '76.63 MB'}
>>>
>>> comic.check_integrity(filename=metaFileCompress['name'])
File is valid?:  "True"
True
>>> comic.check_integrity(filename=metaFileCompress['name'], show=False)
True
```
