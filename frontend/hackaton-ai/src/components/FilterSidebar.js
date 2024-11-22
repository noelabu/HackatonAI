import React, { useState } from "react";

const FilterSidebar = ({ onFilter }) => {
  const [filters, setFilters] = useState({
    minPrice: "",
    maxPrice: "",
    bedrooms: "",
    bathrooms: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters({ ...filters, [name]: value });
  };

  const handleApplyFilter = () => {
    onFilter({
      minPrice: filters.minPrice ? parseInt(filters.minPrice) : null,
      maxPrice: filters.maxPrice ? parseInt(filters.maxPrice) : null,
      bedrooms: filters.bedrooms ? parseInt(filters.bedrooms) : null,
      bathrooms: filters.bathrooms ? parseInt(filters.bathrooms) : null,
    });
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Filter Properties</h2>
      <div className="form-control mb-4">
        <label className="label">
          <span className="label-text">Min Price</span>
        </label>
        <input
          type="number"
          name="minPrice"
          value={filters.minPrice}
          onChange={handleChange}
          className="input input-bordered"
        />
      </div>
      <div className="form-control mb-4">
        <label className="label">
          <span className="label-text">Max Price</span>
        </label>
        <input
          type="number"
          name="maxPrice"
          value={filters.maxPrice}
          onChange={handleChange}
          className="input input-bordered"
        />
      </div>
      <div className="form-control mb-4">
        <label className="label">
          <span className="label-text">Bedrooms</span>
        </label>
        <input
          type="number"
          name="bedrooms"
          value={filters.bedrooms}
          onChange={handleChange}
          className="input input-bordered"
        />
      </div>
      <div className="form-control mb-4">
        <label className="label">
          <span className="label-text">Bathrooms</span>
        </label>
        <input
          type="number"
          name="bathrooms"
          value={filters.bathrooms}
          onChange={handleChange}
          className="input input-bordered"
        />
      </div>
      <button onClick={handleApplyFilter} className="btn btn-primary w-full">
        Apply Filters
      </button>
    </div>
  );
};

export default FilterSidebar;
