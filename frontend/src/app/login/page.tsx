'use client';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiRequest } from '../../lib/api-client';
export default function LoginPage() {
 const router = useRouter(); const [email,setEmail]=useState(''); const [password,setPassword]=useState(''); const [error,setError]=useState(''); const [busy,setBusy]=useState(false);
 async function submit(e: FormEvent) { e.preventDefault(); setBusy(true); setError(''); try { await apiRequest('/auth/login', {method:'POST', body: JSON.stringify({email,password})}); router.push('/kaizen'); router.refresh(); } catch(err) { setError(err instanceof Error ? err.message : 'Đăng nhập thất bại'); } finally { setBusy(false); } }
 return <main className="shell"><h1>Đăng nhập Kaizen AI</h1><form className="card" onSubmit={submit}><label>Email<br/><input type="email" required value={email} onChange={e=>setEmail(e.target.value)}/></label><p/><label>Mật khẩu<br/><input type="password" required value={password} onChange={e=>setPassword(e.target.value)}/></label><p/>{error && <p role="alert">{error}</p>}<button disabled={busy}>{busy?'Đang đăng nhập...':'Đăng nhập'}</button></form></main>;
}
