#v.0.1.1
import cv2
import numpy as np

class HistogramTracker:
    def __init__(self):
        self.bbox = None
        self.roi_hist = None
        self.tracker_initialized = False

    def init(self, frame, initial_bbox):
        self.bbox = initial_bbox
        x, y, w, h = self.bbox
        roi = frame[y:y+h, x:x+w]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        self.roi_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
        self.roi_hist = cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)
        self.tracker_initialized = True

    def update(self, frame):
        if not self.tracker_initialized:
            raise ValueError("Tracker has not been initialized with a bounding box.")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1) #dst = cv2.calcBackProject(images, channels, hist, ranges, scale)
        
        ret, new_bbox = cv2.meanShift(dst, self.bbox, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1))
        
        if ret:
            self.bbox = new_bbox
            return True, self.bbox
        else:
            return False, self.bbox