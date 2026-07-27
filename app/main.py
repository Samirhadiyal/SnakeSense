# app/main.py
import io
import json
import os
from contextlib import asynccontextmanager
from PIL import Image

import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_b0
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import PredictionResponse, SpeciesPrediction, TriageRequest, TriageResponse
from app.species_db import get_species_info

# Global variables
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL = None
CLASS_MAPPING = {}

# Preprocessing transform (matching notebook validation setup)
eval_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL, CLASS_MAPPING
    
    # Path setup based on project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    checkpoint_path = os.path.join(project_root, "checkpoints", "best_model.pth")
    mapping_path = os.path.join(project_root, "models", "class_mapping.json")
    
    # 1. Load class mapping JSON
    if os.path.exists(mapping_path):
        with open(mapping_path, "r") as f:
            raw_mapping = json.load(f)
            CLASS_MAPPING = {int(k): str(v) for k, v in raw_mapping.items()}
    else:
        raise FileNotFoundError(f"Class mapping missing at {mapping_path}")
    
    num_classes = len(CLASS_MAPPING)
    
    # 2. Instantiate EfficientNet B0 architecture
    model = efficientnet_b0(weights=None)
    num_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(num_features, num_classes)
    
    # 3. Load trained weights
    if os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
        state_dict = checkpoint["model_state_dict"] if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint else checkpoint
        model.load_state_dict(state_dict)
        model.to(DEVICE)
        model.eval()
        MODEL = model
        print(f"==================================================")
        print(f"✅ Model loaded successfully on {DEVICE}")
        print(f"Classes: {num_classes} | Checkpoint: {checkpoint_path}")
        print(f"==================================================")
    else:
        raise FileNotFoundError(f"Model checkpoint missing at {checkpoint_path}")
        
    yield
    
    # Clean up on shutdown
    MODEL = None

app = FastAPI(
    title="SnakeSense AI API",
    description="Safety-first snake species classification and snakebite emergency guidance platform",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local testing / mobile app connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "device": str(DEVICE),
        "model_loaded": MODEL is not None,
        "classes_registered": len(CLASS_MAPPING)
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")
        
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")
        
    tensor_img = eval_transform(image).unsqueeze(0).to(DEVICE)
    
    with torch.no_grad():
        outputs = MODEL(tensor_img)
        probabilities = torch.softmax(outputs, dim=1)
        top_probs, top_indices = torch.topk(probabilities, k=min(3, len(CLASS_MAPPING)))
        
    predictions = []
    top_confidence = top_probs[0][0].item() * 100
    is_low_confidence = top_confidence < 40.0  # Threshold trigger for uncertain state
    
    for rank, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0]), start=1):
        species_name = CLASS_MAPPING.get(idx.item(), "Unknown")
        meta = get_species_info(species_name)
        
        predictions.append(
            SpeciesPrediction(
                rank=rank,
                scientific_name=species_name,
                common_name=meta["common_name"],
                local_names=meta["local_names"],
                confidence_percentage=round(prob.item() * 100, 2),
                toxicity_status=meta["toxicity_status"],
                venom_type=meta["venom_type"],
                is_big_four=meta["is_big_four"]
            )
        )
        
    return PredictionResponse(
        status="success",
        is_low_confidence=is_low_confidence,
        top_predictions=predictions,
        safety_disclaimer="CRITICAL DISCLAIMER: AI image predictions are non-diagnostic. Never handle wild snakes or delay medical evaluation based on prediction confidence."
    )

@app.post("/triage", response_model=TriageResponse)
def clinical_triage(request: TriageRequest):
    if not request.bitten:
        return TriageResponse(
            urgency_level="LOW",
            suspected_toxicity="None reported",
            action_protocol={
                "instructions": "No bite reported. Maintain safe distance from snake."
            },
            emergency_contacts=["108 (Ambulance)", "112 (National Emergency)"]
        )
        
    # High/Critical risk logic based on WHO/NCDC guidelines
    is_critical = request.drooping_eyelids or request.difficulty_breathing or request.spontaneous_bleeding
    urgency = "CRITICAL" if is_critical else "HIGH"
    
    suspected = "Systemic Envenoming (Neurotoxic / Haemotoxic)" if is_critical else "Potential Local Envenoming"
    
    dos = [
        "Reassure the victim and keep them completely calm.",
        "Immobilize the bitten limb with a splint or loose bandage.",
        "Remove tight jewelry, rings, watches, or restrictive clothing.",
        "Transport the victim to a facility with Antivenom (ASV) and ICU facilities immediately."
    ]
    
    donts = [
        "DO NOT cut or incision the bite wound.",
        "DO NOT attempt to suck venom by mouth or device.",
        "DO NOT apply a tight tourniquet or tight rope.",
        "DO NOT apply herbal remedies, ice, or chemicals.",
        "DO NOT give the victim alcohol, caffeine, or pain medication."
    ]
    
    return TriageResponse(
        urgency_level=urgency,
        suspected_toxicity=suspected,
        action_protocol={
            "immediate_action": "RUSH TO NEAREST DISTRICT HOSPITAL OR PRIMARY HEALTH CENTER",
            "dos": dos,
            "donts": donts
        },
        emergency_contacts=["108 (Emergency Ambulance)", "112 (National Emergency Response)"]
    )