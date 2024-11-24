'use client';

import { useState } from 'react';
import axios from 'axios'; // Import axios
import { useRouter } from 'next/navigation';

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
  response?: string;
  lister_name: string;
}

export default function ListingPage() {
  const [formData, setFormData] = useState<Property>({
    listing_id: 0, // Assuming a default value, adjust as needed
    property_name: '',
    price: 0,
    location: '',
    bedrooms: 0,
    bathrooms: 0,
    floor_area: 0,
    lot_area: 0,
    property_type: 'house',
    image_path: [],
    lister_name: '',
  });
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log(formData);
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}`+'/add_property_listing', formData);
      console.log('Form submitted successfully:', response.data);
      // if (response.status == 201){
      //   router.push('/');
      // }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'price' || name === 'bedrooms' || name === 'bathrooms' || name === 'floor_area' || name === 'lot_area' 
        ? Number(value) 
        : value
    }));
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newImages = Array.from(e.target.files).map(file => {
        const filePath = `/images/${file.name}`;
        const reader = new FileReader();
        reader.onload = () => {
          const base64Image = reader.result as string;
          // Here you can save the base64 string to local storage or handle it as needed
        };
        reader.readAsDataURL(file);
        console.log(`Saving file to: ${filePath}`);
        return filePath;
      });
      setFormData(prev => ({
        ...prev,
        image_path: [...prev.image_path, ...newImages]
      }));
    }
  };

  const removeImage = (index: number) => {
    setFormData(prev => ({
      ...prev,
      image_path: prev.image_path.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="mockup-browser border bg-base-300" data-theme="light">
      <div className="mockup-browser-toolbar">
      </div>
      <div className="px-4 py-8 bg-base-200">
        <div className="container mx-auto">
          <div className="max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">List a New Property</h1>
            
            <form onSubmit={handleSubmit} className="space-y-6 bg-base-100 p-6 rounded-xl shadow-xl">
              <div>
                <label className="block text-sm font-medium mb-2">Property Name</label>
                <input
                  type="text"
                  name="property_name"
                  value={formData.property_name}
                  onChange={handleChange}
                  className="input input-bordered w-full"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Lister Name</label>
                <input
                  type="text"
                  name="lister_name"
                  value={formData.lister_name}
                  onChange={handleChange}
                  className="input input-bordered w-full"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Price</label>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Location</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Bedrooms</label>
                  <input
                    type="number"
                    name="bedrooms"
                    value={formData.bedrooms}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Bathrooms</label>
                  <input
                    type="number"
                    name="bathrooms"
                    value={formData.bathrooms}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Lot Area (m²)</label>
                  <input
                    type="number"
                    name="lot_area"
                    value={formData.lot_area}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Floor Area (m²)</label>
                  <input
                    type="number"
                    name="floor_area"
                    value={formData.floor_area}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Property Type</label>
                <select
                  name="property_type"
                  value={formData.property_type}
                  onChange={handleChange}
                  className="select select-bordered w-full"
                  required
                >
                  <option value="House">House</option>
                  <option value="Apartment">Apartment</option>
                  <option value="Condo">Condo</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Property Images</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                  className="file-input file-input-bordered w-full"
                />
                {formData.image_path.length > 0 && (
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    {formData.image_path.map((image, index) => (
                      <div key={index} className="relative">
                        <img
                          src={image}
                          alt={`Property image ${index + 1}`}
                          className="w-full h-24 object-cover rounded"
                        />
                        <button
                          type="button"
                          onClick={() => removeImage(index)}
                          className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <button
                type="submit"
                className="btn btn-primary w-full"
              >
                List Property
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
