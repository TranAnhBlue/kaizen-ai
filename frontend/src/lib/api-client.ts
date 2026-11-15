const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:3001/api/v1';
export async function apiGet<T>(path: string): Promise<T> { const response = await fetch(`${BASE}${path}`, { cache: 'no-store', credentials: 'include' }); if (!response.ok) throw new Error(`API error: ${response.status}`); return response.json() as Promise<T>; }
