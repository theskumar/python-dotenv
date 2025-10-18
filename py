import os
import openai # pyright: ignore[reportMissingImports]
from fastapi import FastAPI # type: ignore
from pydantic import BaseModel # pyright: ignore[reportMissingImports]
from typing import List, Literal, Optional
from dotenv import load_dotenv # type: ignore

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialiser l'application FastAPI
app = FastAPI(
    title="AI 3D Presentation Generator API",
    description="API pour générer des présentations 3D en utilisant l'IA.",
    version="1.0.0"
)

# --- Modèles de données Pydantic pour la validation ---
# Ces modèles définissent la structure exacte du JSON que nous attendons de l'IA.

class SceneObject(BaseModel):
    type: Literal["text", "box", "sphere", "cone", "cylinder"]
    content: Optional[str] = None
    position: List[float]
    color: str
    size: Optional[float] = None
    scale: Optional[List[float]] = None
    rotation: Optional[List[float]] = None
    material: Optional[str] = None

class Scene3D(BaseModel):
    cameraPosition: List[float]
    objects: List[SceneObject]
    lighting: dict

class Slide(BaseModel):
    id: int
    title: str
    content: str
    scene3D: Scene3D

class Presentation(BaseModel):
    title: str
    slides: List[Slide]

# --- Service d'IA ---
def generate_presentation_with_ai(topic: str) -> Presentation:
    """
    Appelle l'API OpenAI pour générer la structure de la présentation.
    """
    print(f"Génération d'une présentation sur le thème : '{topic}'...")

    # Un prompt très structuré pour guider l'IA et forcer une sortie JSON
    system_prompt = """
    Tu es un expert en création de présentations 3D immersives. Ton unique mission est de transformer un sujet donné en un objet JSON valide décrivant une présentation.
    Le JSON doit suivre EXACTEMENT la structure Pydantic suivante :
    {
      "title": "string",
      "slides": [
        {
          "id": 1,
          "title": "string",
          "content": "string",
          "scene3D": {
            "cameraPosition": [x, y, z],
            "objects": [
              {
                "type": "text",
                "content": "string",
                "position": [x, y, z],
                "size": 0.5,
                "color": "#FFFFFF"
              },
              {
                "type": "sphere",
                "position": [x, y, z],
                "color": "#4F46E5",
                "material": "emissive"
              }
            ],
            "lighting": { "type": "ambient", "intensity": 0.5 }
          }
        }
      ]
    }
    Génère 2 diapositives pour le sujet donné. Le style doit être moderne, épuré et professionnel.
    Réponds UNIQUEMENT avec l'objet JSON, sans aucun autre texte, ni explication, ni formatage markdown.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Sujet : '{topic}'"}
            ],
            temperature=0.7,
        )
        
        # L'API OpenAI nous garantit un JSON valide grâce à response_format
        presentation_data = response.choices[0].message.content
        
        # Pydantic va valider et parser le JSON dans notre modèle
        validated_presentation = Presentation.model_validate_json(presentation_data)
        print("Génération réussie et validation OK.")
        return validated_presentation

    except Exception as e:
        print(f"Erreur lors de l'appel à l'API OpenAI: {e}")
        # En cas d'erreur, on peut retourner une présentation par défaut ou lever une exception
        raise ValueError("L'IA n'a pas pu générer la présentation.")

# --- Endpoint de l'API ---
class GenerationRequest(BaseModel):
    topic: str

@app.post("/generate-presentation", response_model=Presentation)
async def create_presentation(request: GenerationRequest):
    """
    Endpoint principal qui prend un sujet et retourne une présentation 3D générée par l'IA.
    """
    if not request.topic:
        raise HTTPException(status_code=400, detail="Le sujet est requis.") # type: ignore
    
    try:
        presentation = generate_presentation_with_ai(request.topic)
        return presentation
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue.") # type: ignore

# Pour lancer le serveur : uvicorn main:app --reload
import requests # pyright: ignore[reportMissingModuleSource]

# Vous devriez stocker ce token de manière sécurisée après le flux OAuth
CANVA_API_TOKEN = "votre_token_d_acces_canva"

def get_user_canva_designs():
    headers = {
        "Authorization": f"Bearer {CANVA_API_TOKEN}"
    }
    # L'endpoint de l'API Canva pour lister les designs
    url = "https://api.canva.com/v1/designs"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lève une exception pour les réponses 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à l'API Canva: {e}")
        return None

# Vous pourriez ensuite appeler cette fonction et passer les résultats à votre service d'IA
# pour qu'il transforme le contenu d'un design spécifique en présentation 3D.
