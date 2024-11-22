from fastapi import APIRouter
from pydantic import BaseModel

import pandas as pd
import ast

from app.utils.propguard_validator import RealEstateSafetyAgent
from app.utils.propguard_scorer import QualitativeTrustScorer
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
    bathrooms:int
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
async def add_listing_property(property_form_values:PropertyValues):
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
    "lot_area": property_form_values.lot_area, # in square meters
    "floor_area": property_form_values.floor_area,  # in square meters
    "bedrooms": property_form_values.bedrooms,
    "bathrooms": property_form_values.bathrooms,
    "price": property_form_values.price,
    "images": property_form_values.image_path,
    "lister_name": property_form_values.lister_name,
    "reviews" : ["Professional and responsive, Jeffrey provided detailed answers to my inquiries and accommodated multiple viewing schedules. Highly recommended!!", "Good listings, but some negotiations took longer than expected. Otherwise, a smooth transaction."]
    }
    validation_data = agent.validate_listing(listing_data)
    scorer_agent = QualitativeTrustScorer(agent.llm)
    scorer_data = scorer_agent.evaluate_listing(validation_data)

    #new_data_value = property_form_values
    #new_data_value["response"] = scorer_data[]
    #//add_data_in_csv('/Users/nbunag/Desktop/Projects/HackatonAI/Data/listing_dataset.csv', property_form_values)
    return validation_data

@router.get(
    "/list_property",
    status_code=200
)
async def list_all_listing_property():
    df = pd.read_csv('/Users/nbunag/Desktop/Projects/HackatonAI/Data/Listings_Dataset.csv')
    df['image_path'] = df['image_path'].apply(ast.literal_eval)
    data_as_dicts = df.to_dict(orient='records')
    return data_as_dicts