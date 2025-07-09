// src/PantryForm.js
import React, { useState } from 'react';

function PantryForm() {
  const [item, setItem] = useState('');
  const [quantity, setQuantity] = useState(1);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('https://localhost:5000/api/pantry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "Item Name": item, "Quantity": quantity }),
    });
    setItem('');
    setQuantity(1);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={item} onChange={e => setItem(e.target.value)} placeholder="Item Name" />
      <input type="number" value={quantity} min="1" onChange={e => setQuantity(e.target.value)} />
      <button type="submit">Add Item</button>
    </form>
  );
}

export default PantryForm;