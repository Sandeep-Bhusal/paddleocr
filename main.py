from preprocess import preprocess_image
from ocr_engine import run_ocr
from document_detector import detect_document

def process_document(image_path):
    image = preprocess_image(image_path)
    texts, confidence = run_ocr(image)
    
    print(f"DEBUG - Extracted texts: {texts}")
    print(f"DEBUG - Confidence: {confidence}")

    result = detect_document(texts)
    result["confidence"] = round(confidence, 2)
    result["extracted_texts"] = texts  # Add this for debugging

    return result


if __name__ == "__main__":
    output = process_document(r"images\4.png")
    print(output)
