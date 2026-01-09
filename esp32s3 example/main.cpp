#include <Wire.h>               // Library for I2C communication
#include <Adafruit_GFX.h>       // Core graphics library
#include <Adafruit_SSD1306.h>   // Hardware-specific library for OLED displays
#include "angry.h"              // Custom header file output from script

// --- OLED Display Configuration ---
#define SCREEN_WIDTH 128        // OLED display width, in pixels
#define SCREEN_HEIGHT 64        // OLED display height, in pixels

// --- ESP32-S3 Hardware Pins ---
// Defining custom SDA and SCL pins for the ESP32-S3 I2C bus
#define I2C_SDA 8
#define I2C_SCL 9

#define OLED_RESET     -1       // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C     // Common I2C address for 128x64 OLEDs

// Initialize the Adafruit_SSD1306 object
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

/**
 * Iterates through an array of bitmaps to create an animation effect.
 * @param frames     The 2D array containing the bitmap data
 * @param frameCount Total number of frames in the animation
 */
void playAnimation(const unsigned char frames[][1024], int frameCount) {
  for (int i = 0; i < frameCount; i++) {
    display.clearDisplay();     // Clear the internal buffer
    
    // Draw the current frame bitmap:
    // (x, y, data, width, height, color, background)
    // Note: 'frames[i]' accesses the current 1024-byte image
    display.drawBitmap(0, 0, frames[i], 128, 64, 1, 0); 
    
    display.display();          // Push buffer to the physical screen
    delay(30);                  // Delay to control playback speed (~33 FPS)
  }
}

void setup() {
  Serial.begin(115200);         // Initialize Serial for debugging

  // Initialize I2C with the custom pins defined above
  Wire.begin(I2C_SDA, I2C_SCL);

  // Initialize the OLED display with the specified address
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);                   // Don't proceed, loop forever if screen isn't found
  }

  display.clearDisplay();       // Clear initial splash screen
  display.display();
}

void loop() {
  // Continuously play the "angry" animation
  // angry_data and ANGRY_FRAME_COUNT is defined in angry.h by Gif2OLED script
  playAnimation(angry_data, ANGRY_FRAME_COUNT);
}
