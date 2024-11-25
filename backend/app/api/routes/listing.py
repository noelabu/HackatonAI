from fastapi import APIRouter
from pydantic import BaseModel

import pandas as pd
import ast
import json

from app.utils.propguard_validator import RealEstateSafetyAgent
from app.utils.propguard_scorer import QualitativeTrustScorer
from app.utils.agent_validator import AgentValidator
from app.utils.crossplatform_validator import CrossPlatformValidator
from app.utils.image_validator import ImageValidator
from decouple import config

router = APIRouter()

class PropertyValues(BaseModel):
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
    new_row = pd.DataFrame(new_form_value)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_path, index=False)
    return new_row

@router.post(
    "/add_property",
    status_code=201
)
async def add_listing_property(property_form_values: PropertyValues):
    agent = RealEstateSafetyAgent(
        openai_api_key=config('OPENAI_API_KEY'), 
        google_api_key=config('GOOGLE_API_KEY'), 
        google_cse_id=config('GOOGLE_CSE_ID'), 
        xai_api_key=config('XAI_API_KEY')
    )

    listing_data = {
        "property_name": property_form_values.property_name,
        "property_type": property_form_values.property_type,  # Must be one of: House, Apartment, Condominium
        "location": property_form_values.location,
        "lot_area": property_form_values.lot_area,  # in square meters
        "floor_area": property_form_values.floor_area,  # in square meters
        "bedrooms": property_form_values.bedrooms,
        "bathrooms": property_form_values.bathrooms,
        "price": property_form_values.price,
        "images": [f"../frontend/hackaton-ai/public{x}" for x in property_form_values.image_path],
        "lister_name": property_form_values.lister_name
    }
    
    try:
        validation_data = agent.validate_listing(listing_data)
    except json.JSONDecodeError as e:
        return {
            "error": "Error transforming agent output",
            "details": str(e)
        }

    # scorer_agent = QualitativeTrustScorer(agent.llm)
    # scorer_data = scorer_agent.evaluate_listing(validation_data)

    # new_data_value = property_form_values
    # new_data_value["response"] = scorer_data[]
    # //add_data_in_csv('/Users/nbunag/Desktop/Projects/HackatonAI/Data/listing_dataset.csv', property_form_values)
    return {
        "validation_data": validation_data,
    }

@router.post(
    "/add_property_listing",
    status_code=201
)
async def add_property_listing(property_form_values: PropertyValues):
    agent = RealEstateSafetyAgent(
        openai_api_key=config('OPENAI_API_KEY'), 
        google_api_key=config('GOOGLE_API_KEY'), 
        google_cse_id=config('GOOGLE_CSE_ID'), 
        xai_api_key=config('XAI_API_KEY')
    )

    listing_data = {
        "property_name": property_form_values.property_name,
        "property_type": property_form_values.property_type,  # Must be one of: House, Apartment, Condominium
        "location": property_form_values.location,
        "lot_area": property_form_values.lot_area,  # in square meters
        "floor_area": property_form_values.floor_area,  # in square meters
        "bedrooms": property_form_values.bedrooms,
        "bathrooms": property_form_values.bathrooms,
        "price": property_form_values.price,
        "images": [f"../frontend/hackaton-ai/public{x}" for x in property_form_values.image_path],
        "lister_name": property_form_values.lister_name
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
        #review_agent = ReviewValidator(openai_api_key=config('OPENAI_API_KEY'))
        response_agent_validator = agent.verify_lister(lister_name=listing_data["lister_name"])
        response_cross_platform =  cr_agent.validate_listing(listing_data)
        response_image_validator =  img_agent.validate_images(image_urls=listing_data["images"])
        
        
        validation_data = {
            "agent_verification": response_agent_validator["agent_verification"],
            "cross_platform": response_cross_platform,
            "image_validation": response_image_validator
        }
        scorer_data = scorer_agent.evaluate_listing(image_validation=response_image_validator, cross_platform=response_cross_platform, agent_verification=response_agent_validator)
        return scorer_data

    except json.JSONDecodeError as e:
        return {
            "error": "Error transforming agent output",
            "details": str(e)
        }

    # scorer_agent = QualitativeTrustScorer(agent.llm)
    # scorer_data = scorer_agent.evaluate_listing(validation_data)

    # new_data_value = property_form_values
    # new_data_value["response"] = scorer_data[]
    # //add_data_in_csv('/Users/nbunag/Desktop/Projects/HackatonAI/Data/listing_dataset.csv', property_form_values)

@router.get(
    "/list_property",
    status_code=200
)
async def list_all_listing_property():
    df = pd.read_csv('/Users/nbunag/Desktop/Projects/HackatonAI/Data/Listings_Dataset.csv')
    df['image_path'] = df['image_path'].apply(ast.literal_eval)
    df['response'] = df['response'].apply(lambda x: x.split(","))
    data_as_dicts = df.to_dict(orient='records')
    return data_as_dicts