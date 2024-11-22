import React from "react";

const PropertyCard = ({ property }) => (
  <div className="card bg-base-100 shadow-xl">
    <figure>
      <img src={property.image} alt={property.title} className="h-48 w-full object-cover" />
    </figure>
    <div className="card-body">
      <h2 className="card-title">{property.title}</h2>
      <p className="text-lg font-bold text-primary">{property.price}</p>
      <p>
        {property.bedrooms} Beds • {property.bathrooms} Baths • {property.area}
      </p>
      <div className="card-actions justify-end">
        <button className="btn btn-primary">View Details</button>
      </div>
    </div>
  </div>
);

export default PropertyCard;
