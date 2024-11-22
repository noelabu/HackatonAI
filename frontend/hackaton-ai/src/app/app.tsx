"use client";
import { useState, useEffect } from "react";
import axios from "axios";

interface Property {
  listing_id: number;
  property_name: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  floor_area: number;
  lot_area: number;
  property_type: string;
  image_path: string[];
  response?: string[];
  lister_name: string;
}

const fetchProperties = async (): Promise<Property[]> => {
  try {
    const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/list_property`);
    return response.data;
  } catch (error) {
    console.error("Error fetching properties:", error);
    return [];
  }
};

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [properties, setProperties] = useState<Property[]>([]);

  useEffect(() => {
    const loadProperties = async () => {
      const fetchedProperties = await fetchProperties();
      setProperties(fetchedProperties);
    };
    loadProperties();
  }, []);

  const filteredProperties = properties.filter(property =>
    property.property_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    property.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="mockup-browser border bg-base-300" data-theme="light">
      <div className="mockup-browser-toolbar">
      </div>
      <div className="px-4 py-8 bg-base-200">
        <div className="container mx-auto">
          <div className="space-y-4">
            {filteredProperties.map((property) => (
              <div key={property.listing_id} className="card lg:card-side bg-base-100 shadow-xl">
                <figure className="lg:w-1/3">
                  <div className="carousel w-full">
                    {property.image_path.map((url, index) => (
                      <div key={index} className="carousel-item w-full">
                        <img 
                          src={url}
                          alt={`${property.property_name} - image ${index + 1}`}
                          className="h-full w-full object-cover"
                        />
                      </div>
                    ))}
                  </div>
                </figure>
                <div className="card-body lg:w-2/3">
                  <h2 className="card-title text-2xl">{property.property_name}</h2>
                  <p className="text-2xl font-bold">PHP {property.price.toLocaleString()}</p>
                  <p className="text-lg">{property.location}</p>
                  <p className="text-sm">Listed by: {property.lister_name}</p>
                  <div className="flex gap-6 text-base">
                    <span className="flex items-center gap-1">
                      {property.bedrooms} beds
                    </span>
                    <span className="flex items-center gap-1">
                      {property.bathrooms} baths
                    </span>
                    <span className="flex items-center gap-1">
                      {property.floor_area} m² floor
                    </span>
                    <span className="flex items-center gap-1">
                      {property.lot_area} m² lot
                    </span>
                  </div>
                  <div className="bg-base-200 p-4 rounded-lg mt-2">
                    <h3 className="font-semibold mb-2">PropGuard says:</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {property.response?.map((note, index) => (
                        <li key={index} className="text-sm">{note}</li>
                      ))}
                    </ul>
                    {/* <p>{property.response}</p> */}
                  </div>
                  <div className="card-actions justify-end mt-4">
                    <button className="btn btn-primary">View Details</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}