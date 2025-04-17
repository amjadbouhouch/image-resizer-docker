import requests
import hashlib
import os

from io import BytesIO
from PIL import Image, ImageOps
from flask import Flask, send_file, request, make_response

app = Flask(__name__)

def generate_hashed_filename(url: str, default_ext: str = ".jpg") -> str:
    """Generate a fixed hash-based filename from the URL."""
    hash_object = hashlib.sha256(url.encode())
    return hash_object.hexdigest()[:12] + default_ext  # First 12 chars for brevity

@app.route('/')
def resize_image():
    image_url = request.args.get('url')
    desired_width = int(request.args.get('w', 1024))

    if not image_url:
        return 'No image URL provided.', 400

    try:
        # Try to get filename and extension from URL
        filename = os.path.basename(image_url)
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        if not filename or "." not in filename:
            filename = generate_hashed_filename(image_url, ext)

        # Download image
        response = requests.get(image_url, timeout=5)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        image = ImageOps.exif_transpose(image)  # Fix orientation

        # Resize
        aspect_ratio = image.width / image.height
        desired_height = int(desired_width / aspect_ratio)
        resized_image = image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)

        # Prepare image output
        output = BytesIO()
        resized_image.convert("RGB").save(output, format='JPEG')
        output.seek(0)

        # Create response with cache headers
        resp = make_response(send_file(output, mimetype='image/jpeg', download_name=filename))
        resp.headers['Cache-Control'] = 'public, max-age=31536000'
        return resp

    except Exception as e:
        return f'Error processing image: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8111)
