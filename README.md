# GIF to 128x64 OLED Converter

A Python utility that converts animated `.gif` files into C arrays (`.c` and `.h` files) compatible with Arduino and 128x64 monochrome OLED displays.

## 📝 Overview

Displaying animations on microcontrollers (like Arduino, ESP32, or STM32) requires converting images into raw byte arrays. This script automates that process by:

1.  Scanning the current directory for `.gif` files.
2.  Resizing them to **128x64** pixels.
3.  Converting them to **1-bit monochrome** (black and white).
4.  Exporting them as C arrays suitable for flash storage.

**Note on Size:** To save flash memory on the microcontroller, this script includes a decimation feature that **skips every 3rd frame**, reducing the total animation size by ~33%.

## ⚙️ Prerequisites

You need Python installed on your machine. You also need the **Pillow** library to handle image processing.

```bash
pip install Pillow
```

## 🚀 How to Use

1.  **Place the Script:** Put your python script in a folder.
2.  **Add Images:** Place your `.gif` files in the same folder.
3.  **Run:** Execute the script:
    ```bash
    python Gif2OLED.py
    ```
4.  **Output:** The script will generate a `.c` and `.h` file for every GIF found (e.g., `my_anim.gif` becomes `my_anim.c` and `my_anim.h`).

## 📂 Output Format

### The Header (`.h`)
Contains the frame count definition and the external declaration of the data array.

```c
#ifndef ANIMATION_H
#define ANIMATION_H

#define ANIMATION_FRAME_COUNT 24
extern const unsigned char animation_data[24][1024];

#endif
```

### The Source (`.c`)
Contains the actual byte arrays representing the pixels. The buffer format is **Row-Major**, suitable for generic `drawBitmap` functions.

## ⚡ Arduino Example

Here is how you can use the generated files in your Arduino Sketch.

1.  Copy the generated `.c` and `.h` files into your Arduino project folder.
2.  Use the following logic in your `.ino` file:

```cpp
#include <Arduino.h>
#include <Wire.h>
// Include your display library (e.g., Adafruit_SSD1306)
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Include the generated header file (change filename to match yours)
#include "my_anim.h" 

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
}

void loop() {
  // Loop through frames
  for (int i = 0; i < MY_ANIM_FRAME_COUNT; i++) {
    display.clearDisplay();
    
    // drawBitmap(x, y, data, width, height, color)
    // Note: We access the specific frame [i] from the 2D array
    display.drawBitmap(0, 0, my_anim_data[i], 128, 64, 1);
    
    display.display();
    delay(50); // Adjust animation speed here
  }
}
```

Or

```cpp
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// This header should contain your PROGMEM array: 
// const unsigned char my_anim_data[][1024] PROGMEM = { ... };
#include "my_anim.h" 

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1 
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// --- Function Declaration ---

/**
 * Plays a full animation sequence
 * @param frames     The 2D array stored in Flash memory
 * @param frameCount Total number of frames to play
 */
void playAnimation(const unsigned char frames[][1024], int frameCount) {
  for (int i = 0; i < frameCount; i++) {
    display.clearDisplay();
    
    // drawBitmap(x, y, data, width, height, color)
    // The library automatically handles PROGMEM data pointers
    display.drawBitmap(0, 0, frames[i], 128, 64, SSD1306_WHITE);
    
    display.display();
    delay(30); // ~33 FPS
  }
}

// --- Main Program ---

void setup() {
  // Initialize with the I2C addr 0x3C (common for 128x64 OLEDs)
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for(;;); // Don't proceed, loop forever if display fails
  }
  
  display.clearDisplay();
  display.display();
}

void loop() {
  // Call the function using your data from my_anim.h
  playAnimation(my_anim_data, MY_ANIM_FRAME_COUNT);
  
  delay(1000); // Pause for 1 second before looping the animation
}

```


## 🛠 Technical Details

* **Resolution:** Fixed at 128x64.
* **Thresholding:** Pixels are considered "ON" (white) if R, G, and B are all < 128. Transparent pixels are treated as "OFF".
* **Bit Packing:** MSB (Most Significant Bit) first.
* **Memory Optimization:** The script automatically drops frame indices where `(frame + 1) % 3 == 0`.

## 📄 License

Open Source. Feel free to use and modify.
