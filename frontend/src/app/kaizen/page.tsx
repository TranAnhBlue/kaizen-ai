'use client';
import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api-client';
type Project = {id:string;title:string;description:string;status:string;createdAt:string};
export default function KaizenPage(){
 const [items,setItems]=useState<Project[]>([]),[title,setTitle]=useState(''),[description,setDescription]=useState(''),[error,setError]=useState(''),[loading,setLoading]=useState(true);
 async function reload(){try{setItems(await apiRequest<Project[]>('/kaizen'));setError('');}catch(e){setError(e instanceof Error?e.message:'Lỗi tải dữ liệu');}finally{setLoading(false);}}
 useEffect(()=>{void reload();},[]);
 async function create(e:FormEvent){e.preventDefault();try{await apiRequest('/kaizen',{method:'POST',body:JSON.stringify({title,description})});setTitle('');setDescription('');await reload();}catch(e){setError(e instanceof Error?e.message:'Lỗi tạo sáng kiến');}}
 return <main className="shell"><Link href="/">Trang chủ</Link> · <Link href="/kpi">KPI</Link><h1>Sáng kiến Kaizen</h1>{error&&<p role="alert">{error} — <Link href="/login">Đăng nhập</Link></p>}<form className="card" onSubmit={create}><h2>Tạo sáng kiến</h2><input required maxLength={180} placeholder="Tên sáng kiến" value={title} onChange={e=>setTitle(e.target.value)}/><p/><textarea required maxLength={10000} placeholder="Mô tả vấn đề và ý tưởng cải tiến" value={description} onChange={e=>setDescription(e.target.value)}/><p/><button>Tạo sáng kiến</button></form><div className="card"><h2>Danh sách</h2>{loading?'Đang tải...':items.length===0?'Chưa có sáng kiến':items.map(x=><article key={x.id}><h3><Link href={`/kaizen/${x.id}`}>{x.title}</Link></h3><p>{x.description}</p><small>{x.status}</small><hr/></article>)}</div></main>;
}
