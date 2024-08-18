from numpy import array, sum
import cv2


"""
File:Screen_Regions.py    

Description:
  Class to rectangle areas of the screen to capture along with filters to apply. Includes functions to
  match a image template to the region using opencv 

Author: sumzer0@yahoo.com
"""


class Screen_Regions:
    def __init__(self, screen, templ):
        self.screen = screen
        self.templates = templ

        # Define the thresholds for template matching to be consistent throughout the program
        self.compass_match_thresh = 0.5
        self.navpoint_match_thresh = 0.8
        self.target_thresh = 0.54
        self.target_occluded_thresh = 0.75
        self.sun_threshold = 125
        self.disengage_thresh = 0.45

        # array is in HSV order which represents color ranges for filtering
        self.orange_color_range   = [array([0, 130, 123]),  array([25, 235, 220])]
        self.orange_2_color_range = [array([16, 165, 220]), array([98, 255, 255])]
        self.target_occluded_range= [array([16, 31, 85]),   array([26, 160, 212])]
        self.blue_color_range     = [array([0, 28, 170]),   array([180, 100, 255])]
        self.fss_color_range      = [array([95, 210, 70]),  array([105, 255, 120])]

        self.reg = {}
        # regions with associated filter and color ranges
        # The rect is top left x, y, and bottom right x, y in fraction of screen resolution
        self.reg['compass']   = {'rect': [0.33, 0.65, 0.46, 0.97], 'width': 1, 'height': 1, 'filterCB': self.equalize, 'filter': None}
        self.reg['target']    = {'rect': [0.33, 0.27, 0.66, 0.70], 'width': 1, 'height': 1, 'filterCB': self.filter_by_color, 'filter': self.orange_2_color_range}   # also called destination
        self.reg['target_occluded']    = {'rect': [0.33, 0.27, 0.66, 0.70], 'width': 1, 'height': 1, 'filterCB': self.filter_by_color, 'filter': self.target_occluded_range} 
        self.reg['sun']       = {'rect': [0.30, 0.30, 0.70, 0.68], 'width': 1, 'height': 1, 'filterCB': self.filter_sun, 'filter': None}
        self.reg['disengage'] = {'rect': [0.42, 0.65, 0.60, 0.80], 'width': 1, 'height': 1, 'filterCB': self.filter_by_color, 'filter': self.blue_color_range}
        self.reg['interdicted'] = {'rect': [0.60, 0.1, 0.90, 0.25], 'width': 1, 'height': 1, 'filterCB': self.filter_by_color, 'filter': self.orange_2_color_range}
        self.reg['fss']       = {'rect': [0.5045, 0.7545, 0.532, 0.7955], 'width': 1, 'height': 1, 'filterCB': self.equalize, 'filter': None}
        self.reg['mission_dest']  = {'rect': [0.46, 0.38, 0.65, 0.86], 'width': 1, 'height': 1, 'filterCB': self.equalize, 'filter': None}    
        self.reg['missions']    = {'rect': [0.50, 0.78, 0.65, 0.85], 'width': 1, 'height': 1, 'filterCB': self.equalize, 'filter': None}   
        self.reg['nav_panel']   = {'rect': [0.25, 0.36, 0.60, 0.85], 'width': 1, 'height': 1, 'filterCB': self.equalize, 'filter': None}  
        
        # convert rect from percent of screen into pixel location, calc the width/height of the area
        for i, key in enumerate(self.reg):
            xx = self.reg[key]['rect']
            self.reg[key]['rect'] = [int(xx[0]*screen.screen_width), int(xx[1]*screen.screen_height), 
                                     int(xx[2]*screen.screen_width), int(xx[3]*screen.screen_height)]
            self.reg[key]['width']  = self.reg[key]['rect'][2] - self.reg[key]['rect'][0]
            self.reg[key]['height'] = self.reg[key]['rect'][3] - self.reg[key]['rect'][1]

    def capture_region(self, screen, region_name):
        """ Just grab the screen based on the region name/rect.
        Returns an unfiltered image. """
        return screen.get_screen_region(self.reg[region_name]['rect'])

    def capture_region_filtered(self, screen, region_name):
        """ Grab screen region and call its filter routine.
        Returns the filtered image. """
        scr = screen.get_screen_region(self.reg[region_name]['rect'])
        if self.reg[region_name]['filterCB'] == None:
            # return the screen region untouched in BGRA format.
            return scr
        else:
            # return the screen region in the format returned by the filter.
            return self.reg[region_name]['filterCB'] (scr, self.reg[region_name]['filter'])          

    def match_template_in_region(self, region_name, templ):
        """ Attempt to match the given template in the given region which is filtered using the region filter.
        Returns the filtered image, detail of match and the match mask. """
        img_region = self.capture_region_filtered(self.screen, region_name)    # which would call, reg.capture_region('compass') and apply defined filter
        match = cv2.matchTemplate(img_region, self.templates.template[templ]['image'], cv2.TM_CCOEFF_NORMED)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(match)
        return img_region, (minVal, maxVal, minLoc, maxLoc), match 
    
    def match_template_in_image(self, image, template):
        """ Attempt to match the given template in the (unfiltered) image.
        Returns the original image, detail of match and the match mask. """
        match = cv2.matchTemplate(image, self.templates.template[template]['image'], cv2.TM_CCOEFF_NORMED)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(match)
        return image, (minVal, maxVal, minLoc, maxLoc), match     
    

    def equalize(self, image=None, noOp=None):
        # Load the image in greyscale
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # create a CLAHE object (Arguments are optional).  Histogram equalization, improves constrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img_out = clahe.apply(img_gray)

        return img_out
        
    def filter_by_color(self, image, color_range):
        """Filters an image based on a given color range.
        Returns the filtered image. Pixels within the color range are returned
        their original color, otherwise black."""
        # converting from BGR to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # filte passed in color low, high
        filtered = cv2.inRange(hsv, color_range[0], color_range[1])

        return filtered
 
    # not used
    def filter_bright(self, image=None, noOp=None):
        equalized = self.equalize(image)
        equalized = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)    #hhhmm, equalize() already converts to gray
        equalized = cv2.cvtColor(equalized, cv2.COLOR_BGR2HSV)
        filtered  = cv2.inRange(equalized, array([0, 0, 215]), array([0, 0, 255]))  #only high value

        return filtered
    
    def set_sun_threshold(self, thresh):
        self.sun_threshold = thresh

    # need to compare filter_sun with filter_bright
    def filter_sun(self, image=None, noOp=None):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # set low end of filter to 25 to pick up the dull red Class L stars
        (thresh, blackAndWhiteImage) = cv2.threshold(hsv, self.sun_threshold, 255, cv2.THRESH_BINARY)

        return blackAndWhiteImage

    # percent the image is white
    def sun_percent(self, screen):
        blackAndWhiteImage = self.capture_region_filtered(screen, 'sun')
 
        wht = sum(blackAndWhiteImage == 255)     
        blk = sum(blackAndWhiteImage != 255)

        result = int((wht / (wht+blk))*100)

        return result
