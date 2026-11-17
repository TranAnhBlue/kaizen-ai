'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiGet, apiRequest } from '../../lib/api-client';
type Citation = {number:number;title:string;excerpt:string;documentId:string};
type ChatResponse = {conversationId:string;answer:string;mode:string;citations:Citation[]};
type Message = {role:'user'|'assistant';content:string;citations?:Citation[]};
type Doc = {id:string;title:string;createdAt:string};
export default function Page(){
 const [docs,setDocs]=useState<Doc[]>([]),[messages,setMessages]=useState<Message[]>([]),[question,setQuestion]=useState(''),[conversationId,setConversationId]=useState<string>(),[busy,setBusy]=useState(false),[error,setError]=useState(''),[file,setFile]=useState<File|null>(null);
 const refresh=()=>apiGet<Doc[]>('/ai-chat/documents').then(setDocs).catch(e=>setError(e.message));
 useEffect(()=>{refresh()},[]);
 async function upload(){if(!file)return;setError('');setBusy(true);try{
  if(file.size>5*1024*1024)throw new Error('Tệp tối đa 5 MB');
  const mimeType=file.name.toLowerCase().endsWith('.pdf')?'application/pdf':file.name.toLowerCase().endsWith('.docx')?'application/vnd.openxmlformats-officedocument.wordprocessingml.document':file.name.toLowerCase().endsWith('.txt')?'text/plain':'';
  if(!mimeType)throw new Error('Chỉ hỗ trợ TXT, PDF, DOCX');
  const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
  await apiRequest('/ai-chat/documents',{method:'POST',body:JSON.stringify({title:file.name,mimeType,contentBase64:btoa(binary)})});setFile(null);await refresh();
 }catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 async function ask(){const q=question.trim();if(!q||busy)return;setBusy(true);setError('');setQuestion('');setMessages(m=>[...m,{role:'user',content:q}]);try{
  const result=await apiRequest<ChatResponse>('/ai-chat/ask',{method:'POST',body:JSON.stringify({question:q,conversationId})});setConversationId(result.conversationId);setMessages(m=>[...m,{role:'assistant',content:result.answer,citations:result.citations}]);
 }catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 return <main className="shell"><Link href="/">← Trang chủ</Link><h1>Chatbot tư vấn Kaizen – Tài liệu nội bộ</h1>
 <div className="card"><h2>Kho tài liệu doanh nghiệp</h2><p>Manager/Admin có thể tải TXT, PDF, DOCX (tối đa 5 MB). PDF scan chưa hỗ trợ OCR.</p>
 <input aria-label="Chọn tài liệu" type="file" accept=".txt,.pdf,.docx" onChange={e=>setFile(e.target.files?.[0]??null)}/><button disabled={!file||busy} onClick={upload}>Tải lên và lập chỉ mục</button>
 <ul>{docs.map(d=><li key={d.id}>{d.title}</li>)}</ul></div>
 <div className="card"><h2>Hỏi đáp</h2><p>Chỉ truy xuất dữ liệu trong doanh nghiệp hiện tại. Khi chưa cấu hình LLM, hệ thống chỉ trả về trích đoạn liên quan.</p>
 {messages.map((m,i)=><div key={i} style={{borderBottom:'1px solid #ddd',padding:'12px 0',whiteSpace:'pre-wrap'}}><strong>{m.role==='user'?'Bạn':'Trợ lý'}:</strong> {m.content}
 {m.citations?.length?<details><summary>Nguồn tham khảo ({m.citations.length})</summary><ul>{m.citations.map(c=><li key={c.number}>[{c.number}] {c.title}: {c.excerpt}</li>)}</ul></details>:null}</div>)}
 <textarea aria-label="Câu hỏi" value={question} onChange={e=>setQuestion(e.target.value)} rows={3} maxLength={2000} placeholder="Ví dụ: Quy trình PDCA áp dụng như thế nào?" style={{width:'100%'}}/>
 <button disabled={busy||!question.trim()} onClick={ask}>{busy?'Đang xử lý...':'Gửi câu hỏi'}</button></div>
 {error?<p role="alert" style={{color:'crimson'}}>{error}</p>:null}</main>
}
