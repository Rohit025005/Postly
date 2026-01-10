# app/images.py
import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

# Find project root (one level up from this file)
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

# Helpful debug print (comment out after verifying)
print("app/images.py: loading .env from:", ENV_PATH)

# Load .env (no harm if keys are in system env already)
load_dotenv(dotenv_path=ENV_PATH)

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY    = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Debug prints (helpful while developing; remove later)
print("CLOUDINARY_CLOUD_NAME present?", bool(CLOUD_NAME))
print("CLOUDINARY_API_KEY present?", bool(API_KEY))
print("CLOUDINARY_API_SECRET present?", bool(API_SECRET))

if not (CLOUD_NAME and API_KEY and API_SECRET):
    raise RuntimeError(
        "Missing Cloudinary credentials. Add CLOUDINARY_CLOUD_NAME, "
        "CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET to your .env or environment."
    )

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True
)
