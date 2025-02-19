import cv2
import numpy as np
import sys
import os

np.set_printoptions(threshold=sys.maxsize)

class CrackDetect:
    def __init__(self, crack_darkness=40, fill_threshhold=2, sharpness=50, resolution=3, amount=1, crop_pixels=20):
        self.darkness = crack_darkness
        self.threshhold = fill_threshhold
        self.sharpness = sharpness
        self.resolution = resolution
        self.amount = amount
        self.crop_pixels = crop_pixels

    def __process_image(self, image_path):
        # Read the image
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        # Crop out the bottom crop_pixels rows first
        image = image[:-self.crop_pixels, :]
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Convert to a binary image (black and white) based on darkness threshold
        dark_mask = cv2.inRange(blurred, 0, self.darkness)
        
        # Dilate to fill crack area
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(dark_mask, kernel, iterations=self.threshhold)
        
        # Remove holes in crack area
        filled_img = self.__fill_holes(dilated)
        
        # Erode to separate crack from noise
        kernel = np.ones((3, 3), np.uint8)
        eroded = cv2.erode(filled_img, kernel, iterations=1)
        
        # Remove extra noise spots in non-crack area
        cleaned_img = self.__remove_spots(eroded)
        
        return cleaned_img

    def __remove_spots(self, image):
        # In this context, no inversion is done as the input is already a binary image
        inverted = image
        
        # Label connected components in the inverted image
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted)
        
        # Create a copy of the image to modify
        filled_img = image.copy()
        
        # Order labels by area size, excluding background
        sorted_labels = np.argsort([x[cv2.CC_STAT_AREA] for x in stats[1:]]) + 1
        
        for i in range(1, num_labels):
            if i in sorted_labels[:-self.amount]:
                # Remove the spot by setting it to black
                filled_img[labels == i] = 0
                
        return filled_img

    def __fill_holes(self, image):
        # Invert the binary image
        inverted = cv2.bitwise_not(image)
        
        # Label connected components in the inverted image
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted)
        
        # Create a copy of the image to modify
        filled_img = image.copy()
        
        for i in range(1, num_labels):  # Skip the background label (0)
            area = stats[i, cv2.CC_STAT_AREA]
            max_hole_area = 20000  # Adjust threshold as needed
            if area < max_hole_area:
                # Fill the hole by setting pixels to white
                filled_img[labels == i] = 255
                
        return filled_img

    # Returns True if image contains a crack
    def has_crack(self, image_path):
        cleaned_img = self.__process_image(image_path)
        
        # Label connected components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned_img)
        
        # Check if any crack (component) reaches the required size
        for i in range(1, num_labels):
            width = stats[i, cv2.CC_STAT_WIDTH]
            height = stats[i, cv2.CC_STAT_HEIGHT]
            min_size = 100
            if width > min_size or height > min_size:
                return True
        return False

    # Given an image, returns a set of polygons that outline a crack.
    # Also saves and shows a preview image, and if specified, a DICE subset file.
    def outline_crack(self, image_path, save_subset=False):
        # Process the image
        cleaned_img = self.__process_image(image_path)
        
        # Smooth edges and generate a mask
        blurred = cv2.GaussianBlur(cleaned_img, (13, 13), 0)
        smooth_mask = cv2.inRange(blurred, self.sharpness, 255)
        
        # Get the border contours of the area
        contours, _ = cv2.findContours(smooth_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Approximate the contours to polygons
        approx_polygons = []
        for i in range(self.amount):
            epsilon = self.resolution
            approx_polygons.append(cv2.approxPolyDP(contours[i], epsilon, True))
        
        # For preview, re-read and crop the original image
        original_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        original_image = original_image[:-self.crop_pixels, :]
        preview_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
        polygons = cv2.polylines(preview_image, approx_polygons, True, (0, 255, 0), 2)
        
        file_name = os.path.basename(image_path).split(".")[0] + "_outline.jpg"
        folder_name = os.path.join(os.path.dirname(image_path) + "_results")
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        cv2.imwrite(os.path.join(folder_name, file_name), polygons)
        
        if save_subset:
            height, width = original_image.shape
            aoi = """0 0
0 {0}
{1} {0}
{1} 0""".format(height, width)
            
            exclusions = ''
            for p in approx_polygons:
                poly_string = ''.join(''.join(str(x[0,0]) + ' ' + str(x[0,1])) + '\n\t\t\t\t' for x in p)[:-5]
                exclusions += """
    begin polygon 
        begin vertices
            {}
        end vertices
    end polygon""".format(poly_string)
            
            output = """# Crack detect output
begin region_of_interest
    begin boundary
        begin polygon
            begin vertices
                {}
            end vertices
        end polygon
    end boundary
    begin excluded{}
    end excluded
end region_of_interest""".format(aoi, exclusions)
            with open(file_name + "_subset.txt", "w") as file:
                file.write(output)
                
        return approx_polygons

    # Creates outlines for all images in a folder
    def outline_crack_batch(self, folder_path):
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f)) and 
                 (os.path.splitext(f)[1] in [".tif", ".tiff"])]
        for f in files:
            if self.has_crack(f):
                self.outline_crack(f)

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python crack_detect_batch.py <folder_path> [crack_darkness] [fill_threshhold] [crop_pixels]")
        sys.exit(1)

    folder_path = sys.argv[1]
    # Optional parameters with defaults
    crack_darkness = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    fill_threshhold = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    crop_pixels = int(sys.argv[4]) if len(sys.argv) > 4 else 60

    detector = CrackDetect(crack_darkness=crack_darkness, fill_threshhold=fill_threshhold, crop_pixels=crop_pixels)
    detector.outline_crack_batch(folder_path)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

main()
