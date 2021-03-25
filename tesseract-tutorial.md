### Install Tesseract

1. macOS
```
$ brew install tesseract
```

2. Linux
```
sudo apt-get install tesseract-ocr
```

/usr/share/tesseract-ocr/tessdata/

3. Windows

- https://digi.bib.uni-mannheim.de/tesseract/  Download version after 4.0.0
- Set environmental variable (Path)  eg. ``C:\Program Files(x86)\Tesseract-OCR``

- Folder ``tessdata/`` stores models

  eg. We can copy file ``verify-codes.traineddata`` into this folder to implement the import of model. 

### Install Python Dependencies Library

~~~
$ pip3 install pytesseract
~~~

### Usage
```cs
Page segmentation modes:
  0    Orientation and script detection (OSD) only.
  1    Automatic page segmentation with OSD.
  2    Automatic page segmentation, but no OSD, or OCR.
  3    Fully automatic page segmentation, but no OSD. (Default)
  4    Assume a single column of text of variable sizes.
  5    Assume a single uniform block of vertically aligned text.
  6    Assume a single uniform block of text.
  7    Treat the image as a single text line.
  8    Treat the image as a single word.
  9    Treat the image as a single word in a circle.
 10    Treat the image as a single character.
 11    Sparse text. Find as much text as possible in no particular order.
 12    Sparse text with OSD.
 13    Raw line. Treat the image as a single text line,
                        bypassing hacks that are Tesseract-specific.<br>

OCR Engine modes:
  0    Original Tesseract only.
  1    Neural nets LSTM only.
  2    Tesseract + LSTM.
  3    Default, based on what is available.
```



eg.

psm 8 would give the best result for OCR a single word

psm 6 may give the best result of a block of text



psm's usage eg.

tesseract inputFile output -l lang --psm 8
