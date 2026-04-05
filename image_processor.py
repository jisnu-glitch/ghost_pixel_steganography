from PIL import Image

class ImageProcessor:
    def __init__(self, path=None):
        self.path = path
        self.img = None

    def load_image(self):
        try:
            self.img = Image.open(self.path)
        except FileNotFoundError:
            raise FileNotFoundError("Image not found")

    def get_image(self):
        if self.img:
            return self.img.convert("RGB")
        return None
    
    def save_array(self, array, path):
        Image.fromarray(array).save(path)