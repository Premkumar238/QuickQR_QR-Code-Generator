"""
QuickQR - command line version.

Examples:
    python qr_cli.py website google.com
    python qr_cli.py app "myapp://open/profile"
    python qr_cli.py whatsapp +15551234567 --message "Hi there!"
"""

import argparse
import os
from datetime import datetime

from qr_maker import normalize_website, normalize_whatsapp, make_qr_image, OUTPUT_DIR


def main():
    parser = argparse.ArgumentParser(description="Make a QR code for a website, app link or WhatsApp.")
    sub = parser.add_subparsers(dest="mode", required=True)

    web = sub.add_parser("website", help="Encode a website URL.")
    web.add_argument("url")

    app = sub.add_parser("app", help="Encode an app link.")
    app.add_argument("url")

    wa = sub.add_parser("whatsapp", help="Encode a WhatsApp chat link.")
    wa.add_argument("number", help="Phone number with country code.")
    wa.add_argument("--message", "-m", default="", help="Optional pre-filled message.")

    parser.add_argument("--output", "-o", help="Where to save the png.")

    args = parser.parse_args()

    # figure out what string to put in the QR
    if args.mode in ("website", "app"):
        payload = normalize_website(args.url)
    else:
        payload = normalize_whatsapp(args.number, args.message)

    img = make_qr_image(payload)

    # pick the output path (auto name if not given)
    if args.output:
        path = args.output
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        name = "qr_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        path = os.path.join(OUTPUT_DIR, name)

    img.save(path)
    print("Encoded:", payload)
    print("Saved to:", path)


if __name__ == "__main__":
    main()
