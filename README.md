Usage:

Make sure you have python and numpy installed

In command line:
python crack_detect.py
or
python crack_detect.py <crack-darkness> <fill-threshhold>

The default crack darkness is 40 (maximum grayscale value of the inside of the crack). Higher values will detect lighter cracks and vise versa.
The default fill threshhold is 2. Higher values will increase the size of the outline but may capture incorrect features.

By default, the program will save a preview image and DICE subset file.
