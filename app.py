from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import traceback
from main import process_document

app = FastAPI()

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile) -> str:
    try:
        file_extension = os.path.splitext(upload_file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(TEMP_DIR, file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

@app.post("/ekyc")
async def ekyc_verification(
    id_front: UploadFile = File(...), 
    id_back: UploadFile = File(...)
):
    id_front_path = None
    id_back_path = None
    
    try:
        # Save files temporarily
        id_front_path = save_upload_file(id_front)
        id_back_path = save_upload_file(id_back)
        
        # 1. Perform OCR on ID Front
        print(f"Processing OCR for Front ID: {id_front_path}")
        ocr_result_front = process_document(id_front_path)
        
        # 2. Perform OCR on ID Back
        print(f"Processing OCR for Back ID: {id_back_path}")
        ocr_result_back = process_document(id_back_path)
        
        # Combine OCR results: Merge logic
        # Initialize with front data (primary source for Name, ID, DOB)
        merged_ocr = ocr_result_front.copy()
        
        # Helper to update if missing or empty
        def update_if_missing(key, source):
            if not merged_ocr.get(key) and source.get(key):
                merged_ocr[key] = source[key]
        
        # Fill in missing details from Back ID (especially Issue Date, Expiry)
        update_if_missing('date_of_issue', ocr_result_back)
        update_if_missing('date_of_expiry', ocr_result_back)
        update_if_missing('place_of_birth', ocr_result_back)
        
        # If front failed to extract important fields, fallback to back
        update_if_missing('full_name', ocr_result_back)
        update_if_missing('id_number', ocr_result_back)
        
        # Include raw text from both for auditing
        merged_ocr['raw_text_front'] = ocr_result_front.get('raw_text')
        merged_ocr['raw_text_back'] = ocr_result_back.get('raw_text')
        # Remove individual raw_text to keep it clean, or keep them as 'raw_text_front' etc.
        if 'raw_text' in merged_ocr:
            del merged_ocr['raw_text']

        # Simplify debug info
        merged_ocr['confidence_front'] = ocr_result_front.get('confidence')
        merged_ocr['confidence_back'] = ocr_result_back.get('confidence')
        if 'confidence' in merged_ocr: del merged_ocr['confidence']
        
        response_data = {
            "status": "success",
            "ocr_data": merged_ocr
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )
    finally:
        # Cleanup temp files
        for path in [id_front_path, id_back_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error removing temp file {path}: {e}")

@app.get("/")
def home():
    return {"message": "eKYC System API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
