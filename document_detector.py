from utils import extract_id_number, extract_passport_number

def classify_brunei_id(id_number):
    if id_number.startswith(('50', '51')):
        return "Green", "Foreigner"
    elif id_number.startswith(('30', '31')):
        return "Red", "Permanent Resident"
    elif id_number.startswith(('00', '01')):
        return "Yellow", "Brunei National"
    else:
        return "Unknown", "Unknown"


def detect_document(texts):
    """
    Detect document type: National ID or Passport
    Check for specific keywords to determine document type
    """
    # Convert texts to lowercase for keyword search
    texts_lower = [t.lower() for t in texts]
    all_text = ' '.join(texts_lower)
    
    # Keywords for National ID (Brunei)
    id_keywords = ['kad pengenalan', 'pengenalan', 'negara brunei', 'jantina', 'tarikh lahir']
    
    # Keywords for Passport
    passport_keywords = ['passport', 'pasport']
    
    # Check for National ID keywords first
    for keyword in id_keywords:
        if keyword in all_text:
            id_number = extract_id_number(texts)
            if id_number:
                color, holder = classify_brunei_id(id_number)
                return {
                    "document_type": "National ID",
                    "id_number": id_number,
                    "card_color": color,
                    "holder_type": holder
                }
    
    # Check for Passport keywords
    for keyword in passport_keywords:
        if keyword in all_text:
            passport_no = extract_passport_number(texts)
            if passport_no:
                return {
                    "document_type": "Passport",
                    "passport_number": passport_no
                }
    
    # Fallback: try to extract ID number (more likely to be on ID card)
    id_number = extract_id_number(texts)
    if id_number:
        color, holder = classify_brunei_id(id_number)
        return {
            "document_type": "National ID",
            "id_number": id_number,
            "card_color": color,
            "holder_type": holder
        }
    
    # Last resort: try passport number
    passport_no = extract_passport_number(texts)
    if passport_no:
        return {
            "document_type": "Passport",
            "passport_number": passport_no
        }

    return {
        "document_type": "Unknown"
    }
