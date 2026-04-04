
from PIL import Image

class ImageProcessor:
    def __init__(self, path):
        self.path = path
        self.img = None
        self.pixels = None

    # Load image
    def load_image(self):
        try:
            self.img = Image.open(self.path)
            self.pixels = self.img.load()
            print("Image loaded")
        except FileNotFoundError:
            print("Error: Image not found")

    # Show details
    def image_details(self):
        if self.img:
            print("Size:", self.img.size)
            print("Mode:", self.img.mode)
            print("Format:", self.img.format)

    # Modify pixels (LSB example)
    def modify_pixels(self):
        if self.img:
            width, height = self.img.size

            for y in range(min(50, height)):
                for x in range(min(50, width)):
                    r, g, b = self.pixels[x, y]

                    # # Modify LSB of Red channel
                    # r = (r & 0xFE) | 1 
                    
                    self.pixels[x, y] = (r, g, b)

            print("Pixels modified")

    # Save image
    def save_image(self, output_path):
        if self.img:
            self.img.save(output_path)
            print("Image saved as", output_path)


# Use
path= input('enter the path:')
processor = ImageProcessor(path)
processor.load_image()
processor.image_details()
processor.modify_pixels()
processor.save_image("output_path")