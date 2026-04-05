import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk

HEADER_BYTES = 4

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

def encode_message_bits(message: str):
    payload = message.encode("utf-8")
    packet = len(payload).to_bytes(HEADER_BYTES, byteorder="big") + payload
    return np.unpackbits(np.frombuffer(packet, dtype=np.uint8))


def decode_message_bits(bit_stream: np.ndarray):
    header_bits = HEADER_BYTES * 8
    if bit_stream.size < header_bits:
        raise ValueError("Image does not contain a valid message header.")

    msg_length = int.from_bytes(np.packbits(bit_stream[:header_bits]).tobytes(), byteorder="big")
    required_bits = header_bits + msg_length * 8
    if required_bits > bit_stream.size:
        raise ValueError("Image does not contain a complete hidden message.")

    payload_bits = bit_stream[header_bits:required_bits]
    return np.packbits(payload_bits).tobytes().decode("utf-8")


def update_preview(state: dict, img_array: np.ndarray | None):
    if img_array is None:
        state["preview_label"].config(image="", text="Preview Window")
        state["preview_image"] = None
        return

    pil_img = Image.fromarray(img_array)
    pil_img.thumbnail((650, 650))
    tk_img = ImageTk.PhotoImage(pil_img)
    state["preview_label"].config(image=tk_img, text="")
    state["preview_image"] = tk_img


def load_image(state: dict):
    image_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")],
    )
    if not image_path:
        return

    try:
        processor = ImageProcessor(image_path)
        processor.load_image()
        loaded = processor.get_image()
        if loaded is None:
            raise ValueError("Could not process image into RGB format.")

        state["original_array"] = np.array(loaded, dtype=np.uint8)
        state["encrypted_array"] = None
        update_preview(state, state["original_array"])
        h, w, _ = state["original_array"].shape
        max_message_bytes = max(0, (w * h - (HEADER_BYTES * 8)) // 8)
        state["status_var"].set(f"Loaded image: {w}x{h}. Max message size: ~{max_message_bytes} bytes")
    except Exception as exc:
        messagebox.showerror("Image Error", f"Could not load image:\n{exc}")


def encrypt_message(state: dict):
    original_array = state["original_array"]
    if original_array is None:
        messagebox.showwarning("No Image", "Please load a cover image first.")
        return

    message = state["message_box"].get("1.0", "end-1c")
    if not message:
        messagebox.showwarning("No Message", "Please type a message to encrypt.")
        return

    try:
        bits = encode_message_bits(message)
        encrypted = original_array.copy()

        # NumPy slicing focus: only Red channel is used for LSB storage.
        red_flat = encrypted[:, :, 0].reshape(-1)

        if bits.size > red_flat.size:
            raise ValueError("Message is too long for this image size.")

        red_flat[: bits.size] = (red_flat[: bits.size] & 0xFE) | bits
        state["encrypted_array"] = encrypted
        update_preview(state, encrypted)
        state["status_var"].set(f"Encrypted {len(message.encode('utf-8'))} bytes into image.")
    except ValueError as exc:
        messagebox.showerror("Encryption Error", str(exc))
    except Exception as exc:
        messagebox.showerror("Encryption Error", f"Could not encrypt message:\n{exc}")


def save_encrypted_image(state: dict):
    encrypted_array = state["encrypted_array"]
    if encrypted_array is None:
        messagebox.showwarning("Nothing to Save", "Encrypt a message first.")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save Encrypted Image",
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")],
    )
    if not save_path:
        return

    try:
        processor = ImageProcessor()
        processor.save_array(encrypted_array, save_path)
        state["status_var"].set(f"Encrypted image saved: {save_path}")
    except Exception as exc:
        messagebox.showerror("Save Error", f"Could not save image:\n{exc}")


def decrypt_from_image(state: dict):
    image_path = filedialog.askopenfilename(
        title="Select Encrypted Image",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")],
    )
    if not image_path:
        return

    try:
        processor = ImageProcessor(image_path)
        processor.load_image()
        loaded = processor.get_image()
        if loaded is None:
            raise ValueError("Could not process image into RGB format.")

        arr = np.array(loaded, dtype=np.uint8)

        red_bits = (arr[:, :, 0].reshape(-1) & 1).astype(np.uint8)
        decoded_message = decode_message_bits(red_bits)

        state["encrypted_array"] = arr
        update_preview(state, arr)
        state["message_box"].delete("1.0", "end")
        state["message_box"].insert("1.0", decoded_message)
        state["status_var"].set(f"Message decrypted from: {image_path}")
    except Exception as exc:
        messagebox.showerror("Decryption Error", f"Could not decrypt message:\n{exc}")


def build_ui():
    root = tk.Tk()
    root.title("Ghost Pixel Steganography Tool")
    root.geometry("1000x700")
    root.minsize(860, 560)

    status_var = tk.StringVar(value="Load an image, type a message, then encrypt.")

    state = {
        "original_array": None,
        "encrypted_array": None,
        "message_box": None,
        "preview_label": None,
        "preview_image": None,
        "status_var": status_var,
    }

    sidebar = tk.Frame(root, width=280, bg="#2c3e50", padx=16, pady=16)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="GHOST PIXEL",
        fg="white",
        bg="#2c3e50",
        font=("Arial", 14, "bold"),
    ).pack(pady=(4, 12))

    tk.Button(sidebar, text="1. Load Cover Image", command=lambda: load_image(state)).pack(fill=tk.X, pady=4)
    tk.Button(
        sidebar,
        text="2. Encrypt Message",
        command=lambda: encrypt_message(state),
        bg="#27ae60",
        fg="white",
    ).pack(fill=tk.X, pady=4)
    tk.Button(sidebar, text="3. Save Encrypted Image", command=lambda: save_encrypted_image(state)).pack(
        fill=tk.X, pady=4
    )
    tk.Button(
        sidebar,
        text="4. Decrypt From Image",
        command=lambda: decrypt_from_image(state),
        bg="#f39c12",
        fg="white",
    ).pack(fill=tk.X, pady=4)

    tk.Label(sidebar, text="Secret Message", fg="white", bg="#2c3e50", anchor="w").pack(
        fill=tk.X, pady=(14, 4)
    )
    message_box = tk.Text(sidebar, height=10, wrap="word")
    message_box.pack(fill=tk.BOTH, expand=False)
    state["message_box"] = message_box

    workspace = tk.Frame(root, bg="#ecf0f1")
    workspace.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    preview_label = tk.Label(workspace, text="Preview Window", bg="#ecf0f1", font=("Arial", 12))
    preview_label.pack(expand=True)
    state["preview_label"] = preview_label

    tk.Label(workspace, textvariable=status_var, bg="#ecf0f1", fg="#1f2d3a", pady=10).pack(fill=tk.X)

    root.mainloop()

if __name__ == "__main__":
    build_ui()
