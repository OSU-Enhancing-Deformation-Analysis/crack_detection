# Crack detection

Areas within cracks are unsuitable for digital image correlation because the pixels are out of depth from the rest of the image. DICe has tools to exclude such areas from analysis, but manually outlining cracks is tedious and time consuming. The crack detection module is part of the preprocessing segment of our project, with the goal of generating DICe subset files excluding the crack area automatically. These subset.txt files can be imported into DICe directly to exclude the target area, saving time and providing better results from DICe.

## Crack detection algorithm

This program uses the OpenCV image library to detect cracks in materials. The algorithm can be sumarized as follows:

1. All pixels below a certain brightness in the image are highlighted
2. The target areas are then "dilated" and "eroded" (grown and shrank) to smooth edges
3. Any holes in target areas are filled
4. All continuous areas except largest n areas are removed
5. The final areas are outlined

It is important to adjust the crack lightness and fill threshold values depending on the details of the input image for the algorithm to work.

## Result examples

#### Image preview after crack detection:
<img src="https://i.ibb.co/cKcdtTjw/crack-2-outline.jpg" width="80%">

#### DICe interface after importing subsets:
<img src="https://i.ibb.co/YJw8L3W/Screenshot-2025-05-18-221900.png" width="90%">

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
