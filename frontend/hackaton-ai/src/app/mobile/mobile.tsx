"use client";
import { useState } from "react";

interface Property {
  id: number;
  title: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  area: number;
  imageUrl: string;
  communityNotes?: string[];
}

export default function Mobile() {
  const [searchTerm, setSearchTerm] = useState('');
  const [properties] = useState<Property[]>([
    {
      id: 1,
      title: "Modern Apartment in City Center",
      price: 250000,
      location: "Manila, Philippines",
      bedrooms: 2,
      bathrooms: 2,
      area: 85,
      imageUrl: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
      communityNotes: [
        "This property may not be genuine based on generic image of the listing.",
        "The reviews about the property are quite generic and do not provide specific details about the property, which could be a potential red flag.",
        "The overall trust score for this property listing is low."
      ]
    },
    {
      id: 2, 
      title: "Luxury Villa with Pool",
      price: 750000,
      location: "Cebu, Philippines",
      bedrooms: 4,
      bathrooms: 3,
      area: 250,
      imageUrl: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9",
      communityNotes: [
        "Gated community with strict security measures",
        "Property has CCTV coverage and alarm system",
        "Neighborhood has active community watch program"
      ]
    },
    // Add more sample properties as needed
  ]);
  const filteredProperties = properties.filter(property =>
    property.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    property.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-100 p-4">
      <div className="mockup-phone border-primary scale-125">
        <div className="camera"></div> 
        <div className="display">
          <div className="artboard artboard-demo phone-1">
            <div className="px-2 py-4 bg-base-200 h-full overflow-y-auto">
              <div className="space-y-4">
                {filteredProperties.map((property) => (
                  <div key={property.id} className="card bg-base-100 shadow-xl">
                    <figure>
                      <img 
                        src={property.imageUrl}
                        alt={property.title}
                        className="h-48 w-full object-cover"
                      />
                    </figure>
                    <div className="card-body p-4">
                      <h2 className="card-title text-lg">{property.title}</h2>
                      <p className="text-xl font-bold">${property.price.toLocaleString()}</p>
                      <p className="text-sm">{property.location}</p>
                      <div className="flex gap-4 text-sm">
                        <span>{property.bedrooms} beds</span>
                        <span>{property.bathrooms} baths</span>
                        <span>{property.area} m²</span>
                      </div>
                      <div className="bg-base-200 p-3 rounded-lg mt-2">
                        <h3 className="font-semibold text-sm mb-1">PropGuard says:</h3>
                        <ul className="list-disc list-inside space-y-1">
                          {property.communityNotes?.map((note, index) => (
                            <li key={index} className="text-xs">{note}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="card-actions justify-end mt-2">
                        <button className="btn btn-primary btn-sm">View Details</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}