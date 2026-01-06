import requests
import os

BASE_URL = "http://127.0.0.1:8000"
IMAGES_DIR = "images"

def test_home():
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"GET /: {response.status_code}")
        print(response.json())
    except Exception as e:
        print(f"Failed to connect to {BASE_URL}: {e}")

def test_ekyc_identical():
    print("\n--- Testing Identical Images (Fraud Check) ---")
    img_path = os.path.join(IMAGES_DIR, "4.png") # Using 4.png as it was used in original main.py
    
    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        return

    files = {
        'id_front': ('id_front.png', open(img_path, 'rb'), 'image/png'),
        'id_back': ('id_back.png', open(img_path, 'rb'), 'image/png'), # Using same image for back for now
        'selfie': ('selfie.png', open(img_path, 'rb'), 'image/png')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ekyc", files=files)
        print(f"POST /ekyc status: {response.status_code}")
        print("Result:", response.json())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        for f in files.values():
            f[1].close()

def test_ekyc_different():
    print("\n--- Testing Different Images (Verification) ---")
    img1_path = os.path.join(IMAGES_DIR, "4.png")
    img2_path = os.path.join(IMAGES_DIR, "5.png") # Assuming 5.png exists and is different
    
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print(f"One of the files not found: {img1_path}, {img2_path}")
        return

    files = {
        'id_card': ('id_card.png', open(img1_path, 'rb'), 'image/png'),
        'selfie': ('selfie.png', open(img2_path, 'rb'), 'image/png')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ekyc", files=files)
        print(f"POST /ekyc status: {response.status_code}")
        print("Result:", response.json())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        for f in files.values():
            f[1].close()

if __name__ == "__main__":
    test_home()
    test_ekyc_identical()
    # test_ekyc_different() # Optional, might differ too much
