# Crack detection

As part of our projects goal to provide additional preprocessing to images for DIC, the crack detection module takes material images as input and outputs crack outlines. These outlines are exported as subset.txt files which can be directly imported to DICe, allowing users to exclude the crack area from DIC analysis without manual outlining.

## Crack detection algorithm

This program uses the OpenCV image library to detect cracks in materials. The algorithm can be sumarized as follows:

1. All pixels below a certain brightness in the image are highlighted
2. The target areas are then "dilated" and "eroded" (grown and shrank) to smooth edges
3. Any holes in target areas are filled
4. All continuous areas except largest n areas are removed
5. The final areas are outlined

It is important to adjust the crack lightness and fill threshold values depending on the details of the input image for the algorithm to work.

## Result examples

<img src="https://i.ibb.co/cKcdtTjw/crack-2-outline.jpg" width="50%">

<img src="https://i.ibb.co/YJw8L3W/Screenshot-2025-05-18-221900.png" width="50%">

## Usage Instructions

### Single file crack detection:

Make sure you have python and numpy installed

In command line:
```
python crack_detect.py <file-name>
```
or
```
python crack_detect.py <file-name> <crack-lightness> <fill-threshhold> <crack-number>
```

The default crack lightness is 40 (maximum grayscale value of the inside of the crack). Higher values will detect lighter cracks and vice versa.

The default fill threshhold is 2. Higher values will increase the size of the outline but may capture incorrect features.

The default crack number is 1, corresponding to a single (largest) detected crack in the output.

By default, the program will save a preview image and DICE subset file.

EXAMPLE:

```
python crack_detect.py crack_1.tif 40 2 1
```

### Batch file crack detection:

```
python crack_detect_batch.py <folder-name>
```
or
```
python crack_detect_batch.py <folder-name> <crack-lightness> <fill-threshhold> <cropped-pixels>
```

The default cropped pixels is 60 which will be enough to crop out the SEM image labels. Higher values crop out more of the image.

The results will be stored in another folder called <folder_name>_results

## Credits

- [OpenCV](https://opencv.org/) for image processing functions 
