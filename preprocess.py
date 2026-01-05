import cv2
import numpy as np

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Get image dimensions
    height, width = img.shape[:2]
    print(f"DEBUG - Original image size: {width}x{height}")
    
    # Only resize if image is too large
    if max(height, width) > 4000:
        scale = 4000 / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        print(f"DEBUG - Resized to: {new_width}x{new_height}")
    elif max(height, width) < 600:
        # Upscale small images for better OCR of small text
        img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        print(f"DEBUG - Upscaled image for small text")
    
    # Apply bilateral filter to preserve edges while reducing noise
    img = cv2.bilateralFilter(img, 9, 75, 75)
    
    # Convert to LAB and boost L channel for better contrast
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Use CLAHE for better small text visibility
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    enhanced = cv2.merge([l, a, b])
    result = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return result
