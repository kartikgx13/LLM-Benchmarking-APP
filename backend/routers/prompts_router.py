from fastapi import APIRouter,File,UploadFile
from services.prompt_service import save_prompts

router = APIRouter()

@router.post("/prompts/upload")
async def upload_prompts(file: UploadFile = File(...)):
    prompts = await save_prompts(file)

    return {
        "message": "Prompts uploaded successfully",
        "num_prompts": len(prompts),
        "prompts": prompts
    }