# PiFace: The Raspberry PA-Pi Competition 2024/5


## **Summary**
PiFace plans to bring security to every doorstep. It uses AI and facial recognition to identify people to open your main door, via a tiny servo. It can be controlled and monitored via an app, save recognised faces and keeps privacy and accessibility at the forefront of its design for disabled and able-bodied users alike.
We care about your data and convenience - the AI is trained to work while disconnected from WiFi using OpenCV, and all AI data is stored on-device forever.
In addition, the cost of PiFace is minimal, simply being below £75 - less than the cost of a Ring doorbell.
Of course, PiFace uses a RF Receiver and Transceiver operating on 433.92MHz as a normal doorbell to quickly notify residents of the house.
And we're just getting started. We plan to add more modules, such as a feature allowing you to authorise friends and family to open the door. We even plan to add a mic/speaker combo to allow you to talk to visitors. Stay tuned!


---
## **Required Components**
- [**Raspberry Pi 4B**](https://thepihut.com/products/raspberry-pi-4-model-b?variant=41005997392067): The main computer for all tasks carried out. The brain of the physical doorbell. 
- **[Raspberry Pi v2.1 8 MP 1080p Camera Module](https://www.amazon.co.uk/Raspberry-Pi-1080p-Camera-Module/dp/B01ER2SKFS?crid=EWQCPWJ2RHCU&dib=eyJ2IjoiMSJ9.cCVzNWP4xjyQFTcIR9LasyUH5zIkzoaCAiZBG1qMaGM8ys4Okz999PHNKHUvthpbCO4Mgx1XcDH5nSxHcVPtdce4ZOVrSF4sf3ruNVln0W2zHAYrp_b4fWDAaDlnwT-UoECAsqQAspTcAEkeRQZ2c9Z3P_-GjDrJPvDe6_eu8bC39K_Jk86ZcQgxSJf8KeaYITaIBm1H40T3VqFjnj5M2Fd98oyZa3ib4c-0d4HZEGA.YVU6uGcYiw_a2DyBg2c0sHmD5m-DWyFSsHoAsjbho5o&dib_tag=se&keywords=arducam+mini+rpi0w&nsdOptOutParam=true&qid=1736448891&sprefix=arducam+mini+rpi0w,aps,69&sr=8-4&th=1)**: 8MP1080p tiny camera module with a flexible ribbon cable.
- [**Servo SG90**](https://www.aliexpress.com/item/1005006283358420.html?aem_p4p_detail=202503220447121359404794992440002761600&algo_pvid=cb7b5d10-9df9-485a-89c5-4e2496c4b7a9&algo_exp_id=cb7b5d10-9df9-485a-89c5-4e2496c4b7a9-3&pdp_ext_f=%7B%22order%22:%22992%22,%22eval%22:%221%22%7D&pdp_npi=4@dis!GBP!1.17!0.61!!!1.47!0.77!@2103894417426440322095591ee582!12000036603734127!sea!UK!4743784561!X&curPageLogUid=4pH2cj1fAMJ2&utparam-url=scene:search%7Cquery_from:&search_p4p_id=202503220447121359404794992440002761600_1): Lightweight servo motor for operating the latch mechanism (5V).
- [**Simple Pushbutton**](https://www.aliexpress.com/item/32815969627.html?algo_pvid=5e6fa120-61c6-41d0-829f-3ae1ecb56365&algo_exp_id=5e6fa120-61c6-41d0-829f-3ae1ecb56365-9&pdp_ext_f=%7B%22order%22:%22969%22,%22eval%22:%221%22%7D&pdp_npi=4@dis!GBP!0.73!0.68!!!0.92!0.86!@210384b917426440546926621efa5e!64798820553!sea!UK!4743784561!X&curPageLogUid=yfyuccizBiyV&utparam-url=scene:search%7Cquery_from:): Simulates the doorbell press.
- [**Transmitter and Receiver at 433.92MHz**](https://www.aliexpress.com/item/1005006546595170.html?aem_p4p_detail=202503220445177276429019750820002759294&algo_pvid=a9e186f7-2402-4956-bfcd-a56e150dad31&algo_exp_id=a9e186f7-2402-4956-bfcd-a56e150dad31-3&pdp_ext_f=%7B%22order%22:%227%22,%22eval%22:%221%22%7D&pdp_npi=4@dis!GBP!0.64!0.53!!!0.80!0.66!@21038df617426439172642151e4f21!12000037624534135!sea!UK!4743784561!X&curPageLogUid=bGCLOjunSWoX&utparam-url=scene:search%7Cquery_from:&search_p4p_id=202503220445177276429019750820002759294_1): Used to transmit button press. 
- [**Generic speaker:**](https://www.amazon.co.uk/gp/product/B0D9QYFMKR?smid=AIF4G7PLKBOZY&psc=1) Used for the sound of the doorbell.
- [**A low-power, low-cost pi(we had the 3b+ laying around):**](https://thepihut.com/products/raspberry-pi-3-model-b-plus) Used as the receiver module.
- (**Optional: PiSugarL for power - we did not use this.**)


---

## **Connections**
### 1. **Raspberry Pi 4B+**
- **Power Supply**:
  - Connect either a **PiSugarL** to the GPIO pins or use a 5V USB adapter.
- **Camera**:
  - Attach the **RPi Camera Module** to the Raspberry Pi's CSI ribbon cable port.

### 2. **Servo Motor (SG90)**
- **Signal Pin**: Connect to GPIO 17.
- **Power Pin**: Connect to 5V pin.
- **Ground**: Connect to GND pin.

### 3. **Pushbutton**
- **Pin 1**: Connect to GPIO 37.
- **Pin 2**: Connect to 3.3V pin.

### 4. **RF Transmitter**
- **VCC** to 5V on the rPi.
- **GND** to GND.
- **DATA**: Connect to GPIO 27.

### 5. **Receiver Pi**
- Connect the speaker to a sutaible amplifier. Take a side [eg. L or R] and connect it to the pi in the following connections:
- **VCC** to 5V
- **GND** to GND
- **L or R+** to GPIO 27
- Then, connect the receiver using the following:
- **VCC** to 5V
- **GND** to GND
- **DATA** to GPIO 17


---

## Installation

- Install the following dependencies in a virtual enviroment by running the following commands:

`sudo apt update && sudo apt upgrade -y` 

`sudo apt install python3-opencv python3-picamera2 -y  #`

`pip install face-recognition numpy dlib imutils  `

`pip install smtplib email  `

`pip install RPi.GPIO gpiozero ` 

`sudo raspi-config  `

`sudo reboot  `

- Transfer at minimum 100 photos to the "photos" folder.
- Run the `training.py` script and wait for it to finish training the AI. A file named `trained.pickle` will be created.
- To setup email, replace the `from_email_addr`, `to_email_addr` and `from_email_pass` with their corresponding credentials.
- On the receiver, install the same dependencies [albeit opencv and face-recognition related libs] and run `receiver.py`.
- You're done! Congratulations, and enjoy PiFace.




---


## **Power Options**
- Either use a **PiSugarL** or a **USB 5V adapter**. The PiSugar is good for portablilty.

---

## **Next Steps**
- Mic / Speaker
- Website
- Finish developing a mobile app for remote face registration.
