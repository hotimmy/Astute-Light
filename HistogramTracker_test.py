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

        # 顯示選定區域的HSV圖像
        cv2.imshow("HSV ROI", hsv_roi)
        cv2.waitKey(1)

    def update(self, frame):
        if not self.tracker_initialized:
            raise ValueError("Tracker has not been initialized with a bounding box.")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)
        
        # 顯示反向概率圖
        cv2.imshow("Back Projected Image", dst)
        cv2.waitKey(1)  # 延遲1毫秒以顯示圖像
        
        ret, new_bbox = cv2.meanShift(dst, self.bbox, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1))
        
        if ret:
            self.bbox = new_bbox
            return True, self.bbox
        else:
            return False, self.bbox

# 測試部分
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    tracker = HistogramTracker()
    initialized = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if not initialized:
            # 初始化追蹤器，這裡用手動選取的方式
            bbox = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
            tracker.init(frame, bbox)
            initialized = True

        else:
            success, bbox = tracker.update(frame)
            if success:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
