import React, { useState } from 'react';
import axios from 'axios';

function Form() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post("http://127.0.0.1:8000/analyze/", new URLSearchParams({ text }));
    setResult(res.data);
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="space-y-2">
        <textarea value={text} onChange={(e) => setText(e.target.value)} className="w-full border p-2" rows="5" placeholder="Describe your legal issue"></textarea>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">Get Advice</button>
      </form>

      {result && (
        <div className="mt-4">
          <h2 className="font-bold">Classification</h2>
          <pre>{JSON.stringify(result.classification, null, 2)}</pre>
          <h2 className="font-bold">Advice</h2>
          <p>{result.advice}</p>
          <h2 className="font-bold">Lawyers</h2>
          <pre>{JSON.stringify(result.lawyers, null, 2)}</pre>
          <h2 className="font-bold">NGOs</h2>
          <pre>{JSON.stringify(result.ngos, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Form;
