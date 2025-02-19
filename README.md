# Single file crack detection:

Make sure you have python and numpy installed

In command line:
```
python crack_detect.py <file-name>
```
or
```
python crack_detect.py <file-name> <crack-lightness> <fill-threshhold>
```

The default crack lightness is 40 (maximum grayscale value of the inside of the crack). Higher values will detect lighter cracks and vice versa.

The default fill threshhold is 2. Higher values will increase the size of the outline but may capture incorrect features.

The default cropped pixels is 60 which will be enough to crop out the SEM image labels. Higher values crop out more of the image.

By default, the program will save a preview image and DICE subset file.

EXAMPLE:

```
python crack_detect.py crack_1.tif 40 2
```

# BATCH file crack detection:

```
python crack_detect_batch.py <folder-name>
```
or
```
python crack_detect_batch.py <folder-name> <crack-lightness> <fill-threshhold> <cropped-pixels>
```

The results will be stored in another folder called <folder_name>_results
