'use client';
import Link from 'next/link';
import {useEffect,useState} from 'react';
import {useParams} from 'next/navigation';
import {apiRequest} from '../../../lib/api-client';
type Event={id:string;action:string;fromStatus:string|null;toStatus:string;comment:string|null;createdAt:string};
type Project={id:string;title:string;description:string;status:string;auditEvents:Event[]};
type Me={sub:string;tenantId:string;role:'EMPLOYEE'|'MANAGER'|'TENANT_ADMIN'};
const actions:Record<string,string[]>={DRAFT:['SUBMIT'],SUBMITTED:['APPROVE','REJECT'],APPROVED:['START'],IN_PROGRESS:['COMPLETE'],REJECTED:['REOPEN']};
export default function KaizenDetail(){
 const {id}=useParams<{id:string}>(); const [project,setProject]=useState<Project|null>(null),[me,setMe]=useState<Me|null>(null),[comment,setComment]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function reload(){try{const [p,u]=await Promise.all([apiRequest<Project>(`/kaizen/${id}`),apiRequest<Me>('/auth/me')]);setProject(p);setMe(u);setError('');}catch(e){setError(e instanceof Error?e.message:'Lỗi tải dữ liệu');}}
 useEffect(()=>{void reload();},[id]);
 async function change(action:string){if(action==='REJECT'&&!comment.trim()){setError('Cần nhập lý do từ chối');return;}setBusy(true);try{await apiRequest(`/kaizen/${id}/transition`,{method:'PATCH',body:JSON.stringify({action,comment})});setComment('');await reload();}catch(e){setError(e instanceof Error?e.message:'Không thể thay đổi trạng thái');}finally{setBusy(false);}}
 const allowed=(actions[project?.status||'']||[]).filter(a=>!['APPROVE','REJECT','START','COMPLETE','REOPEN'].includes(a)||me?.role!=='EMPLOYEE');
 return <main className="shell"><Link href="/kaizen">← Danh sách Kaizen</Link><h1>{project?.title||'Chi tiết sáng kiến'}</h1>{error&&<p role="alert">{error}</p>}{project&&<><div className="card"><p>{project.description}</p><strong>Trạng thái: {project.status}</strong><p><textarea placeholder="Ghi chú / lý do từ chối" maxLength={2000} value={comment} onChange={e=>setComment(e.target.value)}/></p>{allowed.map(a=><button key={a} disabled={busy} onClick={()=>void change(a)} style={{marginRight:8}}>{a}</button>)}</div><div className="card"><h2>Lịch sử xử lý</h2>{project.auditEvents.length===0?'Chưa có thay đổi':project.auditEvents.map(e=><article key={e.id}><p>{e.action}: {e.fromStatus} → {e.toStatus} · {new Date(e.createdAt).toLocaleString('vi-VN')}</p>{e.comment&&<p>{e.comment}</p>}<hr/></article>)}</div></>}</main>;
}
