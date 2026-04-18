# Ghost Pixel Steganography

Ghost Pixel Steganography is an open-source Python tool designed to conceal secret text messages within image files using Least Significant Bit (LSB) encoding. It features a user-friendly graphical interface, real-time image preview, and built-in analytical visualization to compare original cover images against their steganographic counterparts.

## Features

- **Message Encryption:** Hide text data securely within the red color channel of standard image files.
- **Message Decryption:** Extract previously hidden text from encrypted image files.
- **Graphical Interface:** A clean, intuitive Tkinter-based UI for seamless workflow.
- **Visual Analysis:** Includes a Matplotlib-driven comparison tool that displays a "Ghost Pixel Map" (highlighting data distribution changes) and a "Color Integrity" histogram.
- **Support for Multiple Formats:** Load and save images in common formats (PNG, JPG, JPEG, BMP). 

*(Note: Saving encrypted files defaults to PNG to avoid lossy compression artifacts that corrupt LSB data.)*

## Prerequisites

Before running the application, ensure you have the following dependencies installed in your Python environment:

- Python 3.7+
- NumPy
- Pillow (PIL)
- Matplotlib

## Installation

1. Clone or download the repository to your local machine.
2. Open a terminal or command prompt in the project directory.
3. Install the required packages using pip:

```bash
pip install numpy pillow matplotlib
```

## Usage

1. Run the application from your terminal:

```bash
python ghost_pixel_steganography.py
```

2. **Load Cover Image:** Click the button to select an image from your system.
3. **Write Message:** Type the secret message you want to encode in the text box provided in the sidebar.
4. **Encrypt Message:** Click to embed the text into the loaded image. The application will warn you if the text string is too long for the selected image's dimensions.
5. **Save Encrypted Image:** Save the resulting steganographic image.
6. **Decrypt From Image:** Load a previously saved encrypted image to instantly extract the hidden message into the text box.
7. **Visualize Analysis:** Click to open a Matplotlib window comparing the hidden data distribution and color histograms between the original and steganographic image.

## Technical Details

The application utilizes a Least Significant Bit (LSB) steganography technique. It specifically targets the 0th index (Red) color channel of the image's RGB array structure. The process involves:
1. Encoding the provided string into UTF-8.
2. Generating a 4-byte header indicating the length of the payload.
3. Flattening the target channel's matrix.
4. Overwriting the least significant bit of each pixel value with the corresponding bit from the header and payload sequence.
