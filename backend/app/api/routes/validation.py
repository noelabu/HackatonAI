from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
import json

from app.utils.propguard_scorer import QualitativeTrustScorer
from app.utils.agent_validator import AgentValidator
from app.utils.crossplatform_validator import CrossPlatformValidator
from app.utils.image_validator import ImageValidator
from decouple import config

router = APIRouter()

class PropertyValues(BaseModel):
    lister_name: str
    property_name: str
    location: str
    lot_area: int
    floor_area: int
    bedrooms: int
    bathrooms: int
    property_type: str
    price: float
    image_path: list[str]

@router.get(
    "/agent_validation",
    status_code=202
)
async def validate_agent(agent_name:str):
    
    try:
        agent = AgentValidator(
            openai_api_key=config('OPENAI_API_KEY'),
            xai_api_key=config('XAI_API_KEY')
        )
        response_agent_validator = agent.verify_lister(lister_name=agent_name)

        return response_agent_validator

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=404, detail="Error transforming agent output: " + str(e))

@router.get(
    "/image_validation",
    status_code=202
)
async def validate_image(image_path:list):
    
    try:
        img_agent = ImageValidator()
        response_image_validator =  img_agent.validate_images(image_urls=image_path)
        return response_image_validator

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=404, detail="Error transforming agent output: " + str(e))

@router.post(
    "/cross_platform_validation",
    status_code=201
)
async def validate_cross_platform(property_form_values: PropertyValues):
    try:
        listing_data = {
            "listing_name": property_form_values.lister_name,
            "property_name": property_form_values.property_name,
            "property_type": property_form_values.property_type,  # Must be one of: House, Apartment, Condominium
            "location": property_form_values.location,
            "lot_area": property_form_values.lot_area,  # in square meters
            "floor_area": property_form_values.floor_area,  # in square meters
            "bedrooms": property_form_values.bedrooms,
            "bathrooms": property_form_values.bathrooms,
            "price": property_form_values.price,
            "image_path": property_form_values.image_path,
        }
        cr_agent =CrossPlatformValidator(
            openai_api_key=config('OPENAI_API_KEY')
        )
        response_cross_platform =  cr_agent.validate_listing(listing_data)
        return response_cross_platform

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=404, detail="Error transforming agent output: " + str(e))

@router.post(
    "/validation_scoring",
    status_code=201
)
async def score_validations(
    property_form_values: PropertyValues
):
    listing_data = {
        "listing_name": property_form_values.lister_name,
        "property_name": property_form_values.property_name,
        "property_type": property_form_values.property_type,
        "location": property_form_values.location,
        "lot_area": property_form_values.lot_area,
        "floor_area": property_form_values.floor_area,
        "bedrooms": property_form_values.bedrooms,
        "bathrooms": property_form_values.bathrooms,
        "price": property_form_values.price,
        "image_path": property_form_values.image_path,
    }
    
    try:
        agent = AgentValidator(
            openai_api_key=config('OPENAI_API_KEY'),
            xai_api_key=config('XAI_API_KEY')
        )
        cr_agent =CrossPlatformValidator(
            openai_api_key=config('OPENAI_API_KEY')
        )
        img_agent = ImageValidator()
        scorer_agent = QualitativeTrustScorer()
        response_agent_validator = agent.verify_lister(lister_name=listing_data["listing_name"])
        response_cross_platform =  cr_agent.validate_listing(listing_data)
        response_image_validator =  img_agent.validate_images(image_urls=listing_data["image_path"])

        scorer_data = scorer_agent.evaluate_listing(image_validation=response_image_validator, cross_platform=response_cross_platform, agent_verification=response_agent_validator)
        return scorer_data

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=404, detail="Error transforming agent output: " + str(e))
