# QuickQR

QuickQR is a small Python app that turns a **website**, an **app link**, or a
**WhatsApp** chat into a scannable QR code. You can use it as a desktop app with
a simple window, or straight from the command line.


## What it does

- **Website** – type any URL (e.g. `google.com`) and get a QR for it. If you
  forget the `https://`, it gets added automatically.
- **App link** – encode deep links / custom app schemes like `myapp://open/profile`.
- **WhatsApp** – enter a phone number (with country code) and an optional message.
  Scanning the QR opens a WhatsApp chat with that contact and the message
  already typed in, ready to send.
- **Live preview** – see the QR right away before saving.
- **Save as PNG** – export the QR as an image you can print or share.
- **Open Link** – quickly test that the QR points where you expect.

---

## Tech stack

- **Python 3** – the language everything is written in.
- **tkinter** – Python's built-in GUI toolkit, used for the desktop window
  (no extra install needed).
- **qrcode** – the library that actually builds the QR code.
- **Pillow (PIL)** – handles the image so we can preview it and save it as PNG.
- **argparse** – Python's built-in module that powers the command-line version.

---

## How I built this

1. **Started with the core logic.** I wrote small, plain functions that take
   what the user types and turn it into the final text the QR should hold
   (`normalize_website`, `normalize_whatsapp`, `build_payload`).
2. **Added the QR generation.** `make_qr_image` wraps the `qrcode` library and
   returns a Pillow image with high error-correction so codes still scan even if
   a bit smudged.
3. **Built a GUI on top.** Using tkinter I made a small window with the three
   modes, an input box, buttons, and a live preview area.
4. **Added a CLI too.** The same core functions are reused in `qr_cli.py` so the
   tool works without opening a window — handy for quick or scripted use.

The key idea: the QR-making logic lives in one place and both the GUI and the
CLI just call into it.

---

## How the code works

The project is three files:

| File | What it does |
|------|--------------|
| `qr_maker.py` | The core functions **and** the desktop GUI. |
| `qr_cli.py`   | The command-line version (imports the core functions). |
| `requirements.txt` | The libraries to install. |

### The flow, step by step

1. **You pick a mode and type something** (a URL, app link, or WhatsApp number).
2. **`build_payload()` decides what to encode:**
   - For Website / App Link it calls `normalize_website()`, which adds `https://`
     if there's no scheme, but leaves custom ones like `myapp://` alone.
   - For WhatsApp it calls `normalize_whatsapp()`, which strips everything except
     digits from the number and builds a `https://wa.me/<number>` link. If you
     added a message, it gets URL-encoded and attached as `?text=...`.
3. **`make_qr_image()` creates the QR** from that text using the `qrcode`
   library and returns it as a Pillow image.
4. **In the GUI**, that image is shown in the preview area; **Save as PNG**
   writes it to a file, and **Open Link** opens the encoded link in your browser.
   **In the CLI**, the image is just saved straight to disk.

### Why WhatsApp links look like that

Enter the number **with country code** (e.g. `+1 555 123 4567`). Spaces, dashes,
and brackets are ignored. The tool builds a link such as
`https://wa.me/15551234567?text=Hi%20there%21`, so scanning the QR opens a chat
with that number and the message ready to send.

---

## How to run it

### 1. Install the requirements (one time)

```bash
pip install -r requirements.txt
```

Requires **Python 3.8 or newer**.

### 2a. Run the desktop app (easiest)

```bash
python qr_maker.py
```

Then:
1. Pick a mode: **Website**, **App Link**, or **WhatsApp**.
2. Enter the link (or WhatsApp number + optional message).
3. Click **Generate QR**, then **Save as PNG**.

### 2b. Or use the command line

```bash
# Website
python qr_cli.py website google.com

# App link (custom scheme works too)
python qr_cli.py app "myapp://open/profile"

# WhatsApp with a pre-filled message
python qr_cli.py whatsapp +15551234567 --message "Hi there!"

# Choose a custom output file
python qr_cli.py website example.com -o my_qr.png
```

Generated images are saved to the `qr_codes/` folder by default.
