"use client";
import { useState } from "react";

interface Property {
  id: number;
  title: string;
  price: number;
  location: string;
  bedrooms: number;
  bathrooms: number;
  floorArea: number;
  lotArea: number;
  imageUrls: string[];
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
      floorArea: 85,
      lotArea: 100,
      imageUrls: [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2"
      ],
      communityNotes: [
        "This property is listed by a broker that is ",
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
      floorArea: 250,
      lotArea: 500,
      imageUrls: [
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811"
      ],
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
      </div>
      <div className="px-4 py-8 bg-base-200">
        <div className="container mx-auto">
          <div className="space-y-4">
            {filteredProperties.map((property) => (
              <div key={property.id} className="card lg:card-side bg-base-100 shadow-xl">
                <figure className="lg:w-1/3">
                  <div className="carousel w-full">
                    {property.imageUrls.map((url, index) => (
                      <div key={index} className="carousel-item w-full">
                        <img 
                          src={url}
                          alt={`${property.title} - image ${index + 1}`}
                          className="h-full w-full object-cover"
                        />
                      </div>
                    ))}
                  </div>
                </figure>
                <div className="card-body lg:w-2/3">
                  <h2 className="card-title text-2xl">{property.title}</h2>
                  <p className="text-2xl font-bold">${property.price.toLocaleString()}</p>
                  <p className="text-lg">{property.location}</p>
                  <div className="flex gap-6 text-base">
                    <span className="flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M7 2a2 2 0 00-2 2v12a2 2 0 002 2h6a2 2 0 002-2V4a2 2 0 00-2-2H7zm3 14a1 1 0 100-2 1 1 0 000 2z"/>
                      </svg>
                      {property.bedrooms} beds
                    </span>
                    <span className="flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M5 2a2 2 0 00-2 2v14l4-4h9a2 2 0 002-2V4a2 2 0 00-2-2H5zm10 10H5V4h10v8z"/>
                      </svg>
                      {property.bathrooms} baths
                    </span>
                    <span className="flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0h8v12H6V4z"/>
                      </svg>
                      {property.floorArea} m² floor
                    </span>
                    <span className="flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z"/>
                      </svg>
                      {property.lotArea} m² lot
                    </span>
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