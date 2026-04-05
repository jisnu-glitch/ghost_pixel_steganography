import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
from image_processor import ImageProcessor

HEADER_BYTES = 4
def encode_message_bits(message: str) -> np.ndarray:
    payload = message.encode("utf-8")
    packet = len(payload).to_bytes(HEADER_BYTES, byteorder="big") + payload
    return np.unpackbits(np.frombuffer(packet, dtype=np.uint8))

def decode_message_bits(bit_stream: np.ndarray) -> str:
    header_bits = HEADER_BYTES * 8
    if bit_stream.size < header_bits:
        raise ValueError("Image does not contain a valid message header.")

    msg_length = int.from_bytes(np.packbits(bit_stream[:header_bits]).tobytes(), byteorder="big")
    required_bits = header_bits + msg_length * 8
    if required_bits > bit_stream.size:
        raise ValueError("Image does not contain a complete hidden message.")

    payload_bits = bit_stream[header_bits:required_bits]
    return np.packbits(payload_bits).tobytes().decode("utf-8")

def encrypt_message(state: dict) -> None:
    if state["image_path"] is None:
        messagebox.showwarning("No Image", "Please load a cover image first.")
        return

    message = state["message_box"].get("1.0", "end-1c")
    if not message:
        messagebox.showwarning("No Message", "Please type a message to encrypt.")
        return

    try:
        processor = ImageProcessor(state["image_path"])
        processor.load_image()
        img = processor.get_image()
        original_array = np.array(img, dtype=np.uint8)

        bits = encode_message_bits(message)
        encrypted = original_array.copy()
        red_flat = encrypted[:, :, 0].reshape(-1)

        if bits.size > red_flat.size:
            raise ValueError("Message is too long for this image size.")

        red_flat[: bits.size] = (red_flat[: bits.size] & 0xFE) | bits

        state["encrypted_array"] = encrypted
        state["status_var"].set("Message encrypted and saved as encrypted.png")

    except Exception as exc:
        messagebox.showerror("Encryption Error", str(exc))


def decrypt_from_image(state: dict) -> None:
    image_path = filedialog.askopenfilename(
        title="Select Encrypted Image",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")],
    )
    if not image_path:
        return

    try:
        processor = ImageProcessor(image_path)
        processor.load_image()
        
        img = processor.get_image()
        arr = np.array(img, dtype=np.uint8)
        red_bits = (arr[:, :, 0].reshape(-1) & 1).astype(np.uint8)
        decoded_message = decode_message_bits(red_bits)

        state["message_box"].delete("1.0", "end")
        state["message_box"].insert("1.0", decoded_message)
        state["status_var"].set("Message decrypted successfully")

    except Exception as exc:
        messagebox.showerror("Decryption Error", str(exc))