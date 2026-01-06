import re

def extract_id_number(texts):
    """
    Extract Brunei National ID number (8-12 digits format: XX-XXXXXX or XXXXXXXX)
    Common format: 00-127039, 30-XXXXXX, 50-XXXXXX
    
    Prefixes:
    - 00-01: Brunei National
    - 30-31: Permanent Resident
    - 50-51: Foreigner
    """
    # Patterns for Brunei ID: can have dash or be continuous digits
    patterns = [
        r'\b\d{2}-\d{6}\b',  # Format: XX-XXXXXX (with dash)
        r'\b\d{8,12}\b'  # Format: continuous 8-12 digits
    ]
    
    for text in texts:
        clean = text.replace(" ", "").strip()
        for pattern in patterns:
            match = re.search(pattern, clean)
            if match:
                id_num = match.group()
                # Validate: Check valid Brunei ID prefixes
                valid_prefixes = (
                    ('00', '01'),  # Brunei National
                    ('30', '31'),  # Permanent Resident
                    ('50', '51')   # Foreigner
                )
                if any(id_num.startswith(prefix) for prefix in valid_prefixes):
                    return id_num
    return None


def extract_passport_number(texts):
    """
    Extract passport number from texts.
    Filter out common words that shouldn't be passport numbers.
    """
    # Words to exclude (common document terms)
    exclude_words = {'NEGARA', 'KAD', 'PENGENALAN', 'NAMA', 'JANTINA', 'TARIKH', 'LAHIR', 
                     'WARGANEGARA', 'BRUNEI', 'DARUSSALAM', 'LELAKI', 'PEREMPUAN', 
                     'TEMPAT', 'NEGERI', 'BANGSA'}
    
    pattern = r'\b[A-Z0-9]{6,9}\b'
    
    for text in texts:
        match = re.search(pattern, text)
        if match:
            candidate = match.group()
            # Skip if it's a known exclude word
            if candidate not in exclude_words:
                # Passport numbers typically have letters
                if any(c.isalpha() for c in candidate):
                    return candidate
    return None


def extract_full_name(texts):
    """
    Extract full name from NAMA field
    Usually comes after 'NAMA' or similar label.
    Fallback: Look for text after ID number if NAMA is missing.
    """
    name_parts = []
    capture = False
    
    # Pre-calculate ID number to exclude it from name
    id_num = extract_id_number(texts)
    
    # Check if 'NAMA' keyword exists
    has_nama = any('NAMA' in t.upper() or 'NAME' in t.upper() for t in texts)
    
    start_index = 0
    if not has_nama and id_num:
        # Fallback: Find index of ID number and start capturing after it
        for i, text in enumerate(texts):
            if id_num in text:
                start_index = i + 1
                capture = True
                break
    
    for i, text in enumerate(texts):
        if i < start_index:
            continue

        if not capture and (text.upper() in ['NAMA', 'NAME'] or 'NAMA' in text.upper()):
            capture = True
            continue
        
        if capture:
            # Stop if we hit another label
            if any(keyword in text.upper() for keyword in ['JANTINA', 'TARIKH', 'LAHIR', 'TEMPAT', 'NEGERI', 'WARGANEGARA', 'GENDER', 'DATE', 'MUKIM', 'ALAMAT']):
                break
            
            # Skip document labels and filter small tokens
            if len(text) > 2 and not any(keyword in text.upper() for keyword in 
                                         ['KAD', 'PENGENALAN', 'NEGARA', 'BRUNEI', 'DARUSSALAM', 'NAMA']):
                
                # Exclude if it looks like the ID number we found or generally looks like digits
                if id_num and text.replace(" ","") in id_num.replace(" ",""):
                    continue
                if re.search(r'\d', text): # Name shouldn't typically have digits
                    continue
                    
                name_parts.append(text)
    
    return ' '.join(name_parts) if name_parts else None


def extract_date_of_birth(texts):
    """
    Extract date of birth from TARIKH LAHIR field
    Usually format: DD-MM-YYYY or DDMMYYYY
    """
    date_pattern = r'\b\d{2}-\d{2}-\d{4}\b|\b\d{8}\b'
    
    for i, text in enumerate(texts):
        if text.upper() in ['TARIKH LAHIR', 'TARIKH', 'DATE OF BIRTH']:
            # Check next few texts for date format
            for j in range(i+1, min(i+4, len(texts))):
                if re.search(date_pattern, texts[j]):
                    return texts[j]
    
    # Also check all texts for date pattern
    for text in texts:
        if re.search(date_pattern, text):
            return text
    
    return None


def extract_gender(texts):
    """
    Extract gender from JANTINA field
    Malay: LELAKI (male), PEREMPUAN (female)
    English: MALE, FEMALE
    """
    gender_map = {
        'LELAKI': 'Male',
        'PEREMPUAN': 'Female',
        'MALE': 'Male',
        'FEMALE': 'Female'
    }
    
    for text in texts:
        if text.upper() in gender_map:
            return gender_map[text.upper()]
    
    return None


def extract_birthplace(texts):
    """
    Extract birthplace from NEGERI TEMPAT LAHIR or TEMPAT LAHIR
    """
    birthplace_parts = []
    capture = False
    
    date_pattern = r'\b\d{2}-\d{2}-\d{4}\b|\b\d{8}\b'
    
    for text in texts:
        # Stop capturing if we hit other fields
        if any(keyword in text.upper() for keyword in ['WARGANEGARA', 'KAD', 'PENGENALAN', 'JANTINA', 'TARIKH', 'BANGSA', 'ALAMAT']):
            if capture:
                break
        
        # Start capturing only on "TEMPAT LAHIR" or "NEGERI", avoid "TARIKH LAHIR"
        if 'TARIKH' in text.upper():
            continue

        if 'TEMPAT' in text.upper() or ('NEGERI' in text.upper() and 'LAHIR' in text.upper()):
            capture = True
            continue
        
        if capture:
            # Exclude dates
            if re.search(date_pattern, text):
                continue
                
            if len(text) > 2 and text.upper() != 'NEGARA':
                birthplace_parts.append(text)
    
    return ' '.join(birthplace_parts) if birthplace_parts else None
def split_name(full_name):
    """
    Split full name into First, Middle, and Last Name
    """
    if not full_name:
        return {"first_name": None, "middle_name": None, "last_name": None}
    
    parts = full_name.split()
    if len(parts) == 1:
        return {"first_name": parts[0], "middle_name": None, "last_name": None}
    elif len(parts) == 2:
        return {"first_name": parts[0], "middle_name": None, "last_name": parts[1]}
    else:
        return {
            "first_name": parts[0],
            "middle_name": " ".join(parts[1:-1]),
            "last_name": parts[-1]
        }

def extract_date_of_issue(texts):
    """
    Extract Date of Issue (DIKELUARKAN)
    """
    date_pattern = r'\b\d{2}-\d{2}-\d{4}\b|\b\d{8}\b'
    
    for i, text in enumerate(texts):
        if 'DIKELUARKAN' in text.upper() or 'ISSUE' in text.upper():
             # Check next few texts for date format
            for j in range(i+1, min(i+4, len(texts))):
                if re.search(date_pattern, texts[j]):
                    return texts[j]
    return None

def extract_date_of_expiry(texts):
    """
    Extract Date of Expiry (MANSUH)
    """
    date_pattern = r'\b\d{2}-\d{2}-\d{4}\b|\b\d{8}\b'
    
    for i, text in enumerate(texts):
        if 'MANSUH' in text.upper() or 'EXPIRY' in text.upper():
             # Check next few texts for date format
            for j in range(i+1, min(i+4, len(texts))):
                if re.search(date_pattern, texts[j]):
                    return texts[j]
    return None

def extract_all_details(texts):
    """
    Extract all possible details from texts
    """
    full_name = extract_full_name(texts)
    name_details = split_name(full_name)
    
    return {
        "full_name": full_name,
        "first_name": name_details["first_name"],
        "middle_name": name_details["middle_name"],
        "last_name": name_details["last_name"],
        "id_number": extract_id_number(texts),
        "date_of_birth": extract_date_of_birth(texts),
        "place_of_birth": extract_birthplace(texts),
        "gender": extract_gender(texts),
        "date_of_issue": extract_date_of_issue(texts),
        "date_of_expiry": extract_date_of_expiry(texts),
        "raw_text": " ".join(texts)
    }
