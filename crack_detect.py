import cv2
import numpy as np
import sys
import os

np.set_printoptions(threshold=sys.maxsize)

class CrackDetect:
    def __init__(self, crack_darkness=40, fill_threshhold=2, sharpness=50, resolution=3, amount=1):
        self.darkness = crack_darkness
        self.threshhold = fill_threshhold
        self.sharpness = sharpness
        self.resolution = resolution
        self.amount = amount

    def __process_image(self, image_path):
        # Read the image
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)

        # Convert to boolean black and white image
        dark_mask = cv2.inRange(blurred, 0, self.darkness)

        # dilate to fill crack area
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(dark_mask, kernel, iterations=self.threshhold)

        # remove holes in crack area
        filled_img = self.__fill_holes(dilated)

        # erode to seperate crack from noise
        kernel = np.ones((3, 3), np.uint8)
        eroded = cv2.erode(filled_img, kernel, iterations=1)

        # remove extra noise spots in non crack area
        cleaned_img = self.__remove_spots(eroded)

        return cleaned_img

    def __remove_spots(self, image):
        # Fill holes
        # Invert the binary image
        inverted = image

        # Label connected components in the inverted image
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted)

        # Create a copy of the original image to modify
        filled_img = image.copy()

        # Order labels by area size, excluding background
        sorted_labels = np.argsort([x[cv2.CC_STAT_AREA] for x in stats[1:]]) + 1

        for i in range(1, num_labels):
            if i in sorted_labels[:-self.amount]:
                # removed the spot by setting to black
                filled_img[labels == i] = 0

        return filled_img

    def __fill_holes(self, image):
        # Fill holes
        # Invert the binary image
        inverted = cv2.bitwise_not(image)

        # Label connected components in the inverted image
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted)

        # Create a copy of the original image to modify
        filled_img = image.copy()

        for i in range(1, num_labels):  # Skip the background label (0)
            # Get the size of the connected component
            area = stats[i, cv2.CC_STAT_AREA]

            # Define a threshold to identify holes (e.g., ignore very large black regions)
            max_hole_area = 20000  # Adjust this threshold based on your image
            if area < max_hole_area:
                # Fill the hole: set all pixels in this component to white in the original image
                    filled_img[labels == i] = 255

        return filled_img

    # returns True if image contains a crack
    def has_crack(self, image_path):
        cleaned_img = self.__process_image(image_path)

        # Label connected components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned_img)

        # Check if any crack (component) reaches required size
        for i in range(1, num_labels):
            width = stats[i, cv2.CC_STAT_WIDTH]
            height = stats[i, cv2.CC_STAT_HEIGHT]

            min_size = 100
            if(width > min_size or height > min_size):
                return True
            
        return False

    # given an image, returns a set of polygons that outline a crack on the image.
    # also saves and shows a preview image, and if specified, a DICE subset file 
    def outline_crack(self, image_path, save_subset=False):
        cleaned_img = self.__process_image(image_path)
        # smooth edges
        blurred = cv2.GaussianBlur(cleaned_img, (13, 13), 0)
        smooth_mask = cv2.inRange(blurred, self.sharpness, 255)

        # get border contour of area
        contours, _ = cv2.findContours(smooth_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Approximate the contours to polygons
        approx_polygons = []
        for i in range(min(self.amount, len(contours))):
            # epsilon = RESOLUTION * cv2.arcLength(contours[i], True)  # Adjust epsilon for precision
            epsilon = self.resolution
            approx_polygons.append(cv2.approxPolyDP(contours[i], epsilon, True))

        # Draw polygon on image for preview
        original_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        preview_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
        polygons = cv2.polylines(preview_image, approx_polygons, True, (0, 255, 0), 2)

        file_name = os.path.basename(image_path).split(".")[0]
        cv2.imwrite(file_name + "_outline.jpg", polygons)
        cv2.imshow("result", polygons)

        if(save_subset==True):
            #     # Save polygon as DICe subset file

            # area of interest is the entire image
            height, width = original_image.shape
            aoi = """0 0
                        0 {0}
                        {1} {0}
                        {1} 0""".format(height, width)
            
            # exclusions are the polygons generated
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

def main():
    detector = None
    if (len(sys.argv) < 2):
        print("Not enough arguments. Command line usage is the following:")
        print("python crack_detect.py <input image> [crack darkness] [fill threshhold] [crack number]")
        return -1
    elif(len(sys.argv) == 2):
        detector = CrackDetect()
    elif(len(sys.argv) == 3):
        detector = CrackDetect(crack_darkness=int(sys.argv[2]))
    elif(len(sys.argv) == 4):
        detector = CrackDetect(crack_darkness=int(sys.argv[2]), fill_threshhold=int(sys.argv[3]))
    elif(len(sys.argv) == 5):
        detector = CrackDetect(crack_darkness=int(sys.argv[2]), fill_threshhold=int(sys.argv[3]), amount=int(sys.argv[4]))
    
    if(detector.has_crack(sys.argv[1])):
        print("Crack detected")
        detector.outline_crack(sys.argv[1], save_subset=True)
    else:
        print("No crack detected")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

main()