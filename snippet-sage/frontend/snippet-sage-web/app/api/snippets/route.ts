import { NextResponse } from "next/server";

export async function GET() {
  const mockSnippets = [
    { id: "1", title: "Hello World", code: 'print("hello")', language: "python" },
    { id: "2", title: "React useState", code: 'const [count, setCount] = useState(0)', language: "jsx" },
  ];
  return NextResponse.json(mockSnippets);
}