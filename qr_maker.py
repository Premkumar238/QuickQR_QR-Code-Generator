"""
QuickQR - small app to make QR codes for websites, app links and WhatsApp.

Just run this file (python qr_maker.py) and a window pops up.
"""

import os
import re
import webbrowser
from datetime import datetime
from urllib.parse import quote

import qrcode
from qrcode.constants import ERROR_CORRECT_H

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


# where we drop the png files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_codes")


def normalize_website(text):
    # add https:// if the user didn't type any scheme
    text = text.strip()
    if not text:
        raise ValueError("Please enter a website or app link.")

    # leave custom app schemes alone (myapp://, intent:// etc)
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", text):
        return text

    return "https://" + text


def normalize_whatsapp(number, message):
    # keep only the digits from the number
    digits = re.sub(r"[^\d]", "", number)
    if not digits:
        raise ValueError("Please enter a valid WhatsApp number (with country code).")

    link = "https://wa.me/" + digits
    message = message.strip()
    if message:
        # text has to be url-encoded otherwise spaces/symbols break it
        link = link + "?text=" + quote(message)
    return link


def build_payload(mode, primary, secondary):
    if mode == "WhatsApp":
        return normalize_whatsapp(primary, secondary)
    return normalize_website(primary)


def make_qr_image(data, fill_color="black", back_color="white"):
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,  # high so it still scans if a bit damaged
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    return img.convert("RGB")


class QuickQRApp:
    def __init__(self, root):
        self.root = root
        self.current_image = None
        self.preview_photo = None
        self.last_payload = None

        root.title("QuickQR")
        root.geometry("520x680")
        root.configure(bg="#0f172a")
        root.resizable(False, False)

        self.setup_styles()
        self.build_ui()
        self.on_mode_change()  # set the first label correctly

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass  # whatever default theme is fine too

        style.configure("TLabel", background="#0f172a", foreground="#e2e8f0", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 22), foreground="#38bdf8")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#94a3b8")
        style.configure("TButton", font=("Segoe UI Semibold", 10), padding=8)
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 11), padding=10)
        style.configure("TRadiobutton", background="#0f172a", foreground="#e2e8f0", font=("Segoe UI", 10))
        style.map("TRadiobutton", background=[("active", "#0f172a")])

    def build_ui(self):
        wrap = tk.Frame(self.root, bg="#0f172a", padx=24, pady=20)
        wrap.pack(fill="both", expand=True)

        ttk.Label(wrap, text="QuickQR", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text="Turn a website, app link or WhatsApp into a QR code.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(0, 16))

        # the 3 mode buttons at the top
        self.mode = tk.StringVar(value="Website")
        modes = tk.Frame(wrap, bg="#0f172a")
        modes.pack(anchor="w", pady=(0, 14))
        for label in ("Website", "App Link", "WhatsApp"):
            ttk.Radiobutton(
                modes,
                text=label,
                value=label,
                variable=self.mode,
                command=self.on_mode_change,
            ).pack(side="left", padx=(0, 16))

        # main input box
        self.primary_label = ttk.Label(wrap, text="Website URL")
        self.primary_label.pack(anchor="w")
        self.primary_entry = self._make_entry(wrap)
        self.primary_entry.pack(fill="x", ipady=7, pady=(4, 12))

        # second box, only shown for WhatsApp (the message)
        self.secondary_label = ttk.Label(wrap, text="Message (optional)")
        self.secondary_entry = self._make_entry(wrap)

        # buttons row
        self.btn_frame = tk.Frame(wrap, bg="#0f172a")
        self.btn_frame.pack(fill="x", pady=(4, 16))
        ttk.Button(self.btn_frame, text="Generate QR", style="Accent.TButton",
                   command=self.generate).pack(side="left")
        self.save_btn = ttk.Button(self.btn_frame, text="Save as PNG",
                                   command=self.save, state="disabled")
        self.save_btn.pack(side="left", padx=8)
        self.open_btn = ttk.Button(self.btn_frame, text="Open Link",
                                   command=self.open_link, state="disabled")
        self.open_btn.pack(side="left")

        # the box where the QR shows up
        box = tk.Frame(wrap, bg="#1e293b", highlightthickness=1, highlightbackground="#334155")
        box.pack(fill="both", expand=True, pady=(4, 8))
        self.preview = tk.Label(box, bg="#1e293b", text="Your QR code will appear here",
                                fg="#64748b", font=("Segoe UI", 11))
        self.preview.pack(fill="both", expand=True, padx=10, pady=10)

        self.status = ttk.Label(wrap, text="", style="Sub.TLabel")
        self.status.pack(anchor="w")

    def _make_entry(self, parent):
        # small helper so the two entries look the same
        return tk.Entry(
            parent, font=("Segoe UI", 11), bg="#1e293b", fg="#f1f5f9",
            insertbackground="#f1f5f9", relief="flat", highlightthickness=1,
            highlightbackground="#334155", highlightcolor="#38bdf8",
        )

    def on_mode_change(self):
        mode = self.mode.get()
        self.primary_entry.delete(0, "end")

        if mode == "Website":
            self.primary_label.config(text="Website URL")
            self.hide_secondary()
        elif mode == "App Link":
            self.primary_label.config(text="App link (https:// or myapp://)")
            self.hide_secondary()
        else:
            # WhatsApp needs the extra message box
            self.primary_label.config(text="WhatsApp number (with country code)")
            self.show_secondary()

    def show_secondary(self):
        self.secondary_label.pack(anchor="w", before=self.btn_frame)
        self.secondary_entry.pack(fill="x", ipady=7, pady=(4, 12), before=self.btn_frame)

    def hide_secondary(self):
        self.secondary_entry.delete(0, "end")
        self.secondary_label.pack_forget()
        self.secondary_entry.pack_forget()

    def generate(self):
        try:
            payload = build_payload(
                self.mode.get(),
                self.primary_entry.get(),
                self.secondary_entry.get(),
            )
        except ValueError as e:
            messagebox.showwarning("Missing info", str(e))
            return

        self.current_image = make_qr_image(payload)
        self.last_payload = payload

        # show a resized copy in the window (NEAREST keeps the squares sharp)
        display = self.current_image.resize((320, 320), Image.NEAREST)
        self.preview_photo = ImageTk.PhotoImage(display)
        self.preview.config(image=self.preview_photo, text="")

        self.save_btn.config(state="normal")
        self.open_btn.config(state="normal")
        self.status.config(text="Encoded: " + payload)

    def save(self):
        if self.current_image is None:
            return

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        default_name = "qr_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        path = filedialog.asksaveasfilename(
            initialdir=OUTPUT_DIR,
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
        )
        if not path:
            return  # user closed the dialog

        self.current_image.save(path)
        self.status.config(text="Saved to " + path)

    def open_link(self):
        # quick way to check the QR points to the right place
        if self.last_payload:
            webbrowser.open(self.last_payload)


def main():
    root = tk.Tk()
    QuickQRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
