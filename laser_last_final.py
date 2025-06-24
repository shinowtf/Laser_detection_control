import pigpio
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

# Servo angle to pulse width conversion
def set_servo_angle(pin, angle):
    angle = max(0, min(180, angle))
    pulsewidth = int(500 + (angle / 180.0) * 2000)
    pi.set_servo_pulsewidth(pin, pulsewidth)

# Track current angles
set_servo_angle(SERVO_X_PIN, 90)
set_servo_angle(SERVO_Y_PIN, 90)
time.sleep(1)

current_x_angle = 90
current_y_angle = 90

class LaserTracker:
    def __init__(self):
        self.lower_red1 = np.array([0, 120, 200])
        self.upper_red1 = np.array([20, 255, 255])
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
            if radius > 0.5:
                M = cv2.moments(c)
                if M["m00"] != 0:
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
        return frame, center

def main():
    global current_x_angle, current_y_angle

    # Initialize camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    
    tracker = LaserTracker()
    prev_pos = None
    alpha = 0.3  # Smoothing factor for position

    # Define boundary box in center
    frame_w, frame_h = 640, 480
    box_w, box_h = 200, 150
    center_x = frame_w // 2
    center_y = frame_h // 2
    boundary_x1 = center_x - box_w // 2
    boundary_y1 = center_y - box_h // 2
    boundary_x2 = center_x + box_w // 2
    boundary_y2 = center_y + box_h // 2

    try:
        while True:
            frame = picam2.capture_array()
            frame, laser_pos = tracker.detect(frame)

            # Draw boundary box
            cv2.rectangle(frame, (boundary_x1, boundary_y1), (boundary_x2, boundary_y2), (0, 255, 0), 2)

            if laser_pos:
                if prev_pos:
                    laser_pos = (
                        int(prev_pos[0] * (1 - alpha) + laser_pos[0] * alpha),
                        int(prev_pos[1] * (1 - alpha) + laser_pos[1] * alpha),
                    )
                prev_pos = laser_pos

                # Only move if laser is outside the box
                if not (boundary_x1 <= laser_pos[0] <= boundary_x2 and boundary_y1 <= laser_pos[1] <= boundary_y2):
                    offset_x = laser_pos[0] - center_x
                    offset_y = laser_pos[1] - center_y

                    scale = 0.15  # Control sensitivity

                    target_x_angle = current_x_angle - offset_x * scale
                    target_y_angle = current_y_angle + offset_y * scale

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

