const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:3001/api/v1';
export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
 const response = await fetch(`${BASE}${path}`, { ...options, cache: 'no-store', credentials: 'include', headers: { 'Content-Type': 'application/json', ...options.headers } });
 if (!response.ok) { const data = await response.json().catch(() => null); throw new Error(data?.message ?? `API error: ${response.status}`); }
 return response.json() as Promise<T>;
}
export function apiGet<T>(path: string): Promise<T> { return apiRequest<T>(path); }
