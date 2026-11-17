'use client';
import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api-client';
type Run={id:string;kpiCode:string;createdAt:string};
type Event={id:string;action:string;note:string|null;createdAt:string};
type Recommendation={id:string;title:string;kpiCode:string;rationale:string;suggestedAction:string;priority:string;status:string;limitations:string;createdAt:string;evidence:{forecast_run_id?:string;flagged_dates?:{date:string;value:number}[]};events:Event[]};
export default function RecommendationsPage(){
 const [runs,setRuns]=useState<Run[]>([]),[runId,setRunId]=useState(''),[items,setItems]=useState<Recommendation[]>([]),[error,setError]=useState(''),[busy,setBusy]=useState(false),[note,setNote]=useState('');
 async function refresh(){const [r,i]=await Promise.all([apiRequest<Run[]>('/forecasting/runs'),apiRequest<Recommendation[]>('/recommendations')]);setRuns(r);setItems(i);setRunId(x=>x||r[0]?.id||'');}
 useEffect(()=>{void refresh().catch(e=>setError(e instanceof Error?e.message:'Không tải được dữ liệu'));},[]);
 async function generate(e:FormEvent){e.preventDefault();setBusy(true);setError('');try{await apiRequest('/recommendations/generate',{method:'POST',body:JSON.stringify({forecastRunId:runId})});await refresh();}catch(e){setError(e instanceof Error?e.message:'Lỗi tạo đề xuất');}finally{setBusy(false);}}
 async function review(id:string,status:string){setBusy(true);setError('');try{await apiRequest(`/recommendations/${id}/review`,{method:'PATCH',body:JSON.stringify({status,note})});setNote('');await refresh();}catch(e){setError(e instanceof Error?e.message:'Không thể cập nhật');}finally{setBusy(false);}}
 return <main className="shell"><Link href="/">Trang chủ</Link> · <Link href="/forecasting">Dự báo KPI</Link><h1>Đề xuất cải tiến Kaizen</h1><p className="muted">Đề xuất dựa trên quy tắc và kết quả dự báo, phải được con người xác minh và phê duyệt.</p>
 <form className="card" onSubmit={generate}><h2>Tạo đề xuất từ dự báo</h2><label>Lần dự báo <select required value={runId} onChange={e=>setRunId(e.target.value)}><option value="">Chọn lần dự báo</option>{runs.map(r=><option key={r.id} value={r.id}>{r.kpiCode} – {new Date(r.createdAt).toLocaleString('vi-VN')}</option>)}</select></label><p/><button disabled={busy||!runId}>Tạo đề xuất</button></form>
 {error&&<p role="alert">{error}</p>}
 <section className="card"><h2>Danh sách đề xuất ({items.length})</h2><label>Ghi chú phê duyệt / kết quả <textarea value={note} onChange={e=>setNote(e.target.value)} placeholder="Lý do từ chối hoặc kết quả triển khai"/></label>
 {items.map(item=><article key={item.id} className="card"><h3>{item.title}</h3><p>KPI: {item.kpiCode} · Ưu tiên: {item.priority} · Trạng thái: {item.status}</p><p><strong>Cơ sở:</strong> {item.rationale}</p><p><strong>Hành động đề xuất:</strong> {item.suggestedAction}</p><p className="muted">{item.limitations}</p><p>Bằng chứng: {item.evidence.flagged_dates?.map(x=>`${x.date}: ${x.value}`).join('; ')||'Không có'}</p>
 {item.status==='PROPOSED'&&<p><button disabled={busy} onClick={()=>review(item.id,'APPROVED')}>Phê duyệt</button> <button disabled={busy||!note.trim()} onClick={()=>review(item.id,'REJECTED')}>Từ chối</button></p>}
 {item.status==='APPROVED'&&<p><button disabled={busy} onClick={()=>review(item.id,'IMPLEMENTED')}>Đánh dấu đã triển khai</button></p>}
 <details><summary>Lịch sử</summary>{item.events.map(ev=><p key={ev.id}>{new Date(ev.createdAt).toLocaleString('vi-VN')} · {ev.action} · {ev.note||'Không ghi chú'}</p>)}</details></article>)}
 {items.length===0&&<p>Chưa có đề xuất.</p>}</section></main>;
}
