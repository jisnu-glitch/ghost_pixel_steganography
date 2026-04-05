import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

class GhostPixelTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghost Pixel Steganography - B.Tech Edition")
        self.root.geometry("1000x700")
        
        # Data storage
        self.original_img = None  # Original NumPy Array
        self.stego_img = None     # Encoded NumPy Array
        self.tk_image = None      # For UI Display
        
        self._build_ui()

    # --- DUTY 1: UI USING TKINTER ---
    def _build_ui(self):
        # Sidebar for controls
        sidebar = tk.Frame(self.root, width=250, bg="#2c3e50", padx=20, pady=20)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="CONTROLS", fg="white", bg="#2c3e50", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(sidebar, text="1. Load Cover Image", command=self.load_image_file).pack(fill=tk.X, pady=5)
        
        tk.Label(sidebar, text="Secret Message:", fg="white", bg="#2c3e50").pack(anchor="w", pady=(10,0))
        self.msg_input = tk.Text(sidebar, height=4, width=25)
        self.msg_input.pack(pady=5)

        tk.Button(sidebar, text="2. Encode Message", command=self.process_encoding, bg="#27ae60", fg="white").pack(fill=tk.X, pady=5)
        tk.Button(sidebar, text="3. Decode Message", command=self.process_decoding, bg="#f39c12", fg="white").pack(fill=tk.X, pady=5)
        tk.Button(sidebar, text="4. Save Stego Image", command=self.save_stego_file).pack(fill=tk.X, pady=5)
        tk.Button(sidebar, text="5. Visualize Analysis", command=self.show_analysis, bg="#2980b9", fg="white").pack(fill=tk.X, pady=20)

        # Main Workspace for Image Preview
        self.workspace = tk.Frame(self.root, bg="#ecf0f1")
        self.workspace.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        self.canvas_label = tk.Label(self.workspace, text="Preview Window", bg="#ecf0f1", font=("Arial", 12))
        self.canvas_label.pack(expand=True)

    # --- DUTY 2: IMAGE LOADING AND SAVING (PILLOW) ---
    def load_image_file(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp")])
        if path:
            pill_img = Image.open(path).convert("RGB")
            self.original_img = np.array(pill_img)
            self._update_preview(pill_img)
            messagebox.showinfo("Success", "Image loaded into NumPy matrix.")

    def save_stego_file(self):
        if self.stego_img is None:
            return messagebox.showerror("Error", "No encoded image to save!")
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            Image.fromarray(self.stego_img).save(path)
            messagebox.showinfo("Saved", "Stego-image saved successfully as PNG.")

    def _update_preview(self, pil_img):
        pil_img.thumbnail((500, 500))
        self.tk_image = ImageTk.PhotoImage(pil_img)
        self.canvas_label.config(image=self.tk_image, text="")

    # --- DUTY 3: LSB ENCODING & DECODING (NUMPY) ---
    def process_encoding(self):
        if self.original_img is None: return
        
        msg = self.msg_input.get("1.0", tk.END).strip() + "###" # Terminator
        bits = ''.join([format(ord(i), '08b') for i in msg])
        
        flat_img = self.original_img.copy().flatten()
        
        if len(bits) > len(flat_img):
            return messagebox.showerror("Error", "Message too long for this image!")

        # The NumPy Magic: Use bitwise AND to clear LSB, then OR to set the bit
        for i in range(len(bits)):
            flat_img[i] = (flat_img[i] & 254) | int(bits[i])
        
        self.stego_img = flat_img.reshape(self.original_img.shape)
        self._update_preview(Image.fromarray(self.stego_img))
        messagebox.showinfo("Encoded", "Message hidden in Red/Green LSBs.")

    def process_decoding(self):
        if self.stego_img is None: return
        
        flat_img = self.stego_img.flatten()
        bits = [str(flat_img[i] & 1) for i in range(len(flat_img))]
        bit_string = "".join(bits)
        
        chars = [chr(int(bit_string[i:i+8], 2)) for i in range(0, len(bit_string), 8)]
        decoded_msg = "".join(chars).split("###")[0]
        
        messagebox.showinfo("Decoded Message", f"Secret found: {decoded_msg}")

    # --- DUTY 4: VISUALIZE DATA MAPS (MATPLOTLIB) ---
    def show_analysis(self):
        if self.stego_img is None: return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Map showing exactly WHERE the pixels changed
        diff = np.abs(self.original_img.astype(float) - self.stego_img.astype(float))
        ghost_map = np.sum(diff, axis=2) * 255 # Amplify the 1-bit diff to 255
        
        ax1.set_title("Ghost Pixel Map (Data Distribution)")
        ax1.imshow(ghost_map, cmap='magma')
        ax1.axis('off')

        # Histogram showing no statistical shift
        ax2.set_title("Color Integrity (Histogram)")
        ax2.hist(self.original_img.flatten(), bins=50, color='blue', alpha=0.5, label='Original')
        ax2.hist(self.stego_img.flatten(), bins=50, color='red', alpha=0.5, label='Stego')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = GhostPixelTool(root)
    root.mainloop()