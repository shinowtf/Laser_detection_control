import pigpio  # Replaces RPi.GPIO
import time
import cv2
import numpy as np
from picamera2 import Picamera2

# Servo pins
SERVO_X_PIN = 17
SERVO_Y_PIN = 27

# Setup pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon.")
    exit()

# Servo pulse width range: 500–2500 µs typically maps to 0–180°
def set_servo_angle(pin, angle):
    angle = max(0, min(180, angle))
    pulsewidth = int(500 + (angle / 180.0) * 2000)
    pi.set_servo_pulsewidth(pin, pulsewidth)

# Track current angles
current_x_angle = 90
current_y_angle = 90

class LaserTracker:
    def __init__(self):
        self.lower_red1 = np.array([0, 120, 200])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([160, 120, 200])
        self.upper_red2 = np.array([180, 255, 255])
    
    def detect(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        center = None
        if contours:
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 5:
                M = cv2.moments(c)
                if M["m00"] != 0:
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
        return frame, center

def main():
    global current_x_angle, current_y_angle
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    
    tracker = LaserTracker()
    prev_pos = None
    alpha = 0.3  # Coordinate smoothing factor

    try:
        while True:
            frame = picam2.capture_array()
            frame, laser_pos = tracker.detect(frame)

            if laser_pos:
                if prev_pos:
                    laser_pos = (
                        int(prev_pos[0] * (1 - alpha) + laser_pos[0] * alpha),
                        int(prev_pos[1] * (1 - alpha) + laser_pos[1] * alpha),
                    )
                prev_pos = laser_pos

                center_x = 640 // 2
                center_y = 480 // 2
                offset_x = laser_pos[0] - center_x
                offset_y = laser_pos[1] - center_y

                scale = 0.15  # Adjust sensitivity

                if abs(offset_x) > 5 or abs(offset_y) > 5:
                    target_x_angle = current_x_angle - offset_x * scale
                    target_y_angle = current_y_angle + offset_y * scale

                    # Smooth angle update
                    alpha_angle = 0.2
                    smoothed_x = (1 - alpha_angle) * current_x_angle + alpha_angle * target_x_angle
                    smoothed_y = (1 - alpha_angle) * current_y_angle + alpha_angle * target_y_angle

                    current_x_angle = max(0, min(180, smoothed_x))
                    current_y_angle = max(0, min(180, smoothed_y))

                    set_servo_angle(SERVO_X_PIN, current_x_angle)
                    set_servo_angle(SERVO_Y_PIN, current_y_angle)

            cv2.imshow("Laser Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Tracking stopped.")

    finally:
        picam2.stop()
        pi.set_servo_pulsewidth(SERVO_X_PIN, 0)
        pi.set_servo_pulsewidth(SERVO_Y_PIN, 0)
        pi.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

