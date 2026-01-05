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
                     'TEMPAT', 'NEGERI'}
    
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
    Usually comes after 'NAMA' or similar label
    """
    name_parts = []
    capture = False
    
    for i, text in enumerate(texts):
        if text.upper() in ['NAMA', 'NAME']:
            capture = True
            continue
        
        if capture:
            # Stop if we hit another label
            if text.upper() in ['JANTINA', 'TARIKH', 'LAHIR', 'TEMPAT', 'NEGERI', 'WARGANEGARA', 'GENDER', 'DATE']:
                break
            
            # Skip document labels and filter small tokens
            if len(text) > 2 and not any(keyword in text.upper() for keyword in 
                                         ['KAD', 'PENGENALAN', 'NEGARA', 'BRUNEI', 'DARUSSALAM']):
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
    
    for text in texts:
        if 'TEMPAT' in text.upper() or 'LAHIR' in text.upper():
            capture = True
            continue
        
        if capture:
            # Stop if we hit another label
            if any(keyword in text.upper() for keyword in ['WARGANEGARA', 'KAD', 'PENGENALAN']):
                break
            
            if len(text) > 2 and text.upper() != 'NEGARA':
                birthplace_parts.append(text)
    
    return ' '.join(birthplace_parts) if birthplace_parts else None
