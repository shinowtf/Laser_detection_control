INSTRUCTION MANUAL 

OVERVIEW 

The  defence technology missile guidance educational kit  is primarily composed of a Raspberry Pi 4 Model B (2GB) as the main processor, running computer vision algorithms via OpenCV. The system captures real-time images using an OV5647 camera Module, connected to the Pi’s CSI ribbon cable interface, with a resolution of 5MP (2592×1944) and a 54° horizontal field of view.
A 650nm red laser pointer (5mW) is integrated for target detection, while two SG90 servo motors control a 3D-printed PLA gimbal chassis (printed at 190–220°C) to adjust the camera’s X/Y axis orientation. The servos operate at 4.8–5V DC with 180° rotation range, driven by the Pi’s GPIO PWM signals.
Power is supplied via a USB Type-C adapter (5V, 2A), and all components are secured with M2.5 screws (3mm length). The Raspberry Pi executes custom Python scripts to process OV564 camera input, detect laser alignment, and adjust the gimbal servos for precise targeting—demonstrating principles image processing, and real-time feedback control.

Please note
1. Electrical Safety
•	Use the correct power supply: Only the provided 5V USB Type-C adapter (2A) to prevent overheating or damage to the Raspberry Pi.
•	Check wiring: Ensure servo motors (SG90) and laser are correctly connected to GPIO pins to avoid short circuits.
2. Mechanical Precautions
•	Secure the gimbal: Tighten M2.5 screws properly to prevent the 3D-printed chassis from loosening during servo movement.
•	Limit servo torque: Avoid forcing servos beyond their 180° range to prevent gear damage.
3. Camera & Software
•	Handle the  carefully: Avoid touching the lens or bending the CSI ribbon cable.
•	Update software regularly: Keep Raspberry Pi OS and OpenCV libraries patched for stability.
4. General Usage
•	Ventilation: Ensure the Raspberry Pi has airflow to prevent overheating during prolonged use.
•	Age appropriateness: Recommend for ages 12+ (or with adult guidance for younger users).
5. Storage & Maintenance
•	Power off before disassembly: Always shut down the Pi before removing components.
•	Store in a dry place: Protect electronics from humidity/dust.

RASBERRYPI INSTALLATION
Please watch below link to understand the operating system installation :
https://youtu.be/2kNmA3-A2sc

Step 1: Hardware Assembly
1.1 Attach the Camera Module
•	Connect the OV5647 Camera to the Raspberry Pi’s CSI port (ribbon cable slot near the HDMI port).
•	Secure the camera in place using the provided mount (3D-printed or included bracket).
1.2 Connect the Servo Motors
•	SG90 Servo Motor (x-axis): Connect to GPIO pin GPIO17 (PWM).
•	SG90 Servo Motor (y-axis): Connect to GPIO pin GPIO27 (PWM).
•	Power the servos via the Raspberry Pi’s 5V pin (ensure total current draw is within limits).
________________________________________
Step 2: Software Setup
2.1 Install Raspberry Pi OS
•	Flash Raspberry Pi OS (Bullseye) to an SD card using Raspberry Pi Imager.
•	Enable SSH, Camera Interface, and I2C via sudo raspi-config.
2.2 Install Dependencies
Open a terminal and run:
bash
Copy
Download
sudo apt update && sudo apt upgrade -y  
sudo apt install python3-opencv   
pip install numpy  
2.3 Download the Project Code
Clone the example script:
bash
Copy
Download
git clone https://github.com/your-repo/rocket-guidance.git  
cd rocket-guidance  
________________________________________
Step 3: Laser Detection Program
3.1 Code Overview
The script (laser_detection.py) performs:
1.	Image Capture: Uses the OV5647 camera.
2.	HSV Filtering: Isolates the red laser point.
3.	Motor Control: Adjusts servo position based on laser centroid.
3.2 Key Steps in the Algorithm
1.	Convert BGR to HSV: Isolate the laser’s red hue.
2.	Thresholding: Define HSV ranges for the laser (e.g., [0-10, 100-255, 100-255]).
3.	Contour Detection: Find the laser’s center coordinates.
4.	Motor Feedback: Move servos to center the laser in the frame.
3.3 Run the Sample Script
1.	Source venv/bin/activate
2.	Download all the related library framework
3.	Run git clone ‘the link’ provided github repository link for sample code: https://github.com/shinowtf/Laser_detection_control/tree/main
4.	Run ‘python3 laser_detection.py’ 
5.	Press ESC or “q” to exit program.
________________________________________
Step 4: Calibration
1.	Adjust HSV Values: Modify hue_min, hue_max, etc., in the code to match your laser’s color.
2.	Test Servo Range: Ensure motors move smoothly within 0–180 degrees.
3.	Align Laser and Camera: Ensure the laser dot is visible in the camera’s frame.
________________________________________
Troubleshooting
•	No Laser Detected: Check camera focus, HSV range, and laser alignment.
•	Servo Jitter: Add a delay (time.sleep(0.1)) between motor signals.
•	Power Issues: Use an external 5V supply if servos draw too much current.
________________________________________
Applications
•	Rocket Guidance: Track a laser to simulate target alignment.
•	STEM Education: Learn OpenCV, GPIO control, and feedback systems.
Enjoy building your Rocket Guidance System! 🚀
For support, contact: [kahchun@gmail.com]
Project Repository: https://github.com/shinowtf/Laser_detection_control/tree/main




