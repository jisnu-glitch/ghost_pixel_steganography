
import tkinter as tk
from tkinter import filedialog, messagebox
from image_processor import ImageProcessor
from ghost_pixel_steganography import encrypt_message, decrypt_from_image


def test_gui():
    """
    Temporary Tkinter GUI for testing encryption and decryption.

    This interface allows:
    - Loading an image
    - Entering a message
    - Encrypting message into image
    - Decrypting message from image
    - Saving encrypted image

    NOTE:
    This GUI is not the final implementation.
    It is only used for development and testing purposes.
    """

    def run_gui():

        # ---------- Shared State ----------
        state = {
            "image_path": None,
            "encrypted_array": None,
            "message_box": None,
            "status_var": None
        }

        # ---------- GUI Functions ----------
        def load_image():
            path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")]
            )
            if not path:
                return

            state["image_path"] = path
            state["status_var"].set(f"Loaded: {path}")

        def encrypt():
            encrypt_message(state)   #  using your function

        def decrypt():
            decrypt_from_image(state)  #  using your function

        def save_image():
            if state["encrypted_array"] is None:
                messagebox.showwarning("Error", "No encrypted image")
                return

            path = filedialog.asksaveasfilename(defaultextension=".png")
            if not path:
                return
            
            processor = ImageProcessor()
            processor.save_array(state["encrypted_array"], path)
            state["status_var"].set(f"Saved: {path}")

        # ---------- GUI ----------
        root = tk.Tk()
        root.title("Steganography Tool")
        root.geometry("500x400")

        tk.Label(root, text="Ghost Pixel Tool", font=("Arial", 16)).pack(pady=10)

        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Button(frame, text="Load Image", command=load_image).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Encrypt", command=encrypt).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Decrypt", command=decrypt).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Save", command=save_image).grid(row=0, column=3, padx=5)

        tk.Label(root, text="Message:").pack()

        text_box = tk.Text(root, height=10, width=50)
        text_box.pack(pady=5)

        # connect GUI to state
        state["message_box"] = text_box

        status = tk.StringVar()
        status.set("Ready")

        state["status_var"] = status

        tk.Label(root, textvariable=status, bd=1, relief="sunken", anchor="w").pack(fill="x", side="bottom")

        root.mainloop()

    run_gui()


if __name__ == "__main__":
    test_gui()