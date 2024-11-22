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

export default function App() {
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
        "This property is listed by a lister that is not verified.",
        "Close to public transportation and shopping centers",
        "Building has backup power generator"
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
    <div className="mockup-browser border bg-base-300" data-theme="light">
      <div className="mockup-browser-toolbar">
        <div className="input">PropGuard</div>
      </div>
      <div className="px-4 py-8 bg-base-200">
        <div className="container mx-auto">
          <div className="space-y-4">
            {filteredProperties.map((property) => (
              <div key={property.id} className="card lg:card-side bg-base-100 shadow-xl">
                <figure className="lg:w-1/3">
                  <img 
                    src={property.imageUrl}
                    alt={property.title}
                    className="h-full w-full object-cover"
                  />
                </figure>
                <div className="card-body lg:w-2/3">
                  <h2 className="card-title text-2xl">{property.title}</h2>
                  <p className="text-2xl font-bold">${property.price.toLocaleString()}</p>
                  <p className="text-lg">{property.location}</p>
                  <div className="flex gap-6 text-base">
                    <span>{property.bedrooms} beds</span>
                    <span>{property.bathrooms} baths</span>
                    <span>{property.area} m²</span>
                  </div>
                  <div className="bg-base-200 p-4 rounded-lg mt-2">
                    <h3 className="font-semibold mb-2">PropGuard says:</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {property.communityNotes?.map((note, index) => (
                        <li key={index} className="text-sm">{note}</li>
                      ))}
                    </ul>
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