import paddle
paddle.set_device('cpu')
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en', # Combined English and numbers
    det_db_thresh=0.3,  # Lower threshold to detect smaller text regions
    det_db_box_thresh=0.5,  # Lower box threshold for small boxes
    det_limit_side_len=960,  # Increase to process more detail
    det_limit_type='min'  # Use min for detailed detection
)

def run_ocr(image):
    result = ocr.predict(image)

    texts = []
    confidences = []

    print(f"DEBUG - Raw OCR result type: {type(result)}")

    # Handle the new result format - it's a list with a dict inside
    if result and len(result) > 0:
        result_dict = result[0]

        # Extract rec_texts and rec_scores from the dictionary
        if isinstance(result_dict, dict):
            rec_texts = result_dict.get('rec_texts', [])
            rec_scores = result_dict.get('rec_scores', [])

            print(f"DEBUG - rec_texts: {rec_texts}")
            print(f"DEBUG - rec_scores: {rec_scores}")

            texts = rec_texts
            confidences = rec_scores

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    print(f"DEBUG - Extracted texts: {texts}")
    print(f"DEBUG - Average confidence: {avg_confidence}")

    return texts, avg_confidence
