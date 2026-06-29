"use client";
import { useEffect, useState } from "react";

type Snippet = { id: string; title: string; code: string; language: string };

export default function Home() {
  const [snippets, setSnippets] = useState<Snippet[]>([]);

  useEffect(() => {
    fetch("/api/snippets")
      .then((res) => res.json())
      .then(setSnippets);
  }, []);

  return (
    <main className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Snippet-Sage</h1>
      <div className="grid gap-4">
        {snippets.map((s) => (
          <div key={s.id} className="border p-4 rounded shadow bg-white">
            <h2 className="font-semibold">{s.title}</h2>
            <pre className="bg-gray-100 p-2 mt-2 rounded text-sm">{s.code}</pre>
          </div>
        ))}
      </div>
    </main>
  );
}