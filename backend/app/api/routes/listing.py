from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

import pandas as pd
import ast
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

class PropertyValuesResponse(BaseModel):
    listing_id: int
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
    response: str

def add_data_in_csv(csv_path, new_form_value):
    df = pd.read_csv(csv_path)
    new_form_value["listing_id"] = len(df) + 1
    new_row = pd.DataFrame(new_form_value)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_path, index=False)
    return new_row

@router.post(
    "/add_property_listing",
    status_code=201
)
async def add_property_listing(property_form_values: PropertyValues):

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
        listing_data["response"] = ",\n".join(scorer_data["recommendations"])
        add_data_in_csv('../data/listing.csv', listing_data)
        return scorer_data

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=404, detail="Error transforming agent output: " + str(e))

@router.get(
    "/property_listing",
    status_code=200
)
async def list_all_listing_property():
    try:
        df = pd.read_csv('../data/listing.csv')
        df['image_path'] = df['image_path'].apply(ast.literal_eval)
        df['response'] = df['response'].apply(lambda x: x.split(","))
        data_as_dicts = df.to_dict(orient='records')
        return data_as_dicts
    except Exception as e:
        raise HTTPException(status_code=404, detail="Error listing all properties from database: " + str(e))