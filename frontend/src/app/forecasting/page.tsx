'use client';
import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api-client';
type Definition={code:string;name:string;unit:string};
type Point={id:string;forecastDate:string;value:string;lower:string;upper:string;warning:boolean};
type Run={id:string;kpiCode:string;model:string;createdAt:string;trainingPoints:number;holdoutPoints:number;metrics:{mae:number;rmse:number;wape_percent:number|null};anomalies:{date:string;value:number;residual:number}[];limitations:string;values:Point[]};
export default function ForecastingPage(){
 const [defs,setDefs]=useState<Definition[]>([]),[code,setCode]=useState(''),[horizon,setHorizon]=useState(7),[runs,setRuns]=useState<Run[]>([]),[current,setCurrent]=useState<Run|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 useEffect(()=>{void (async()=>{try{const [d,r]=await Promise.all([apiRequest<Definition[]>('/kpi/definitions'),apiRequest<Run[]>('/forecasting/runs')]);setDefs(d);setCode(d[0]?.code??'');setRuns(r);setCurrent(r[0]??null);}catch(e){setError(e instanceof Error?e.message:'Không tải được dữ liệu');}})();},[]);
 async function predict(e:FormEvent){e.preventDefault();setBusy(true);setError('');try{const run=await apiRequest<Run>('/forecasting/predict',{method:'POST',body:JSON.stringify({code,horizon})});setCurrent(run);setRuns(x=>[run,...x]);}catch(e){setError(e instanceof Error?e.message:'Dự báo thất bại');}finally{setBusy(false);}}
 return <main className="shell"><Link href="/">Trang chủ</Link> · <Link href="/kpi">KPI Analytics</Link><h1>Dự báo năng suất và chất lượng</h1><p className="muted">Mô hình baseline xu hướng tuyến tính. Cần ít nhất 8 ngày dữ liệu liên tục, không bỏ ngày.</p>
 <form className="card" onSubmit={predict}><h2>Chạy dự báo</h2><label>Chỉ số KPI <select required value={code} onChange={e=>setCode(e.target.value)}><option value="">Chọn KPI</option>{defs.map(d=><option value={d.code} key={d.code}>{d.name} ({d.unit})</option>)}</select></label><p/><label>Số ngày dự báo <input type="number" min={1} max={30} value={horizon} onChange={e=>setHorizon(Number(e.target.value))}/></label><p/><button disabled={busy||!code}>{busy?'Đang xử lý...':'Dự báo'}</button></form>
 {error&&<p role="alert">{error}</p>}
 {current&&<section className="card"><h2>Kết quả {current.kpiCode}</h2><p>Model: {current.model} · Số ngày học: {current.trainingPoints} · Số ngày đánh giá: {current.holdoutPoints}</p><p>MAE: {current.metrics.mae} · RMSE: {current.metrics.rmse} · WAPE: {current.metrics.wape_percent===null?'Không xác định':`${current.metrics.wape_percent}%`}</p><div style={{overflowX:'auto'}}><table><thead><tr><th>Ngày</th><th>Dự báo</th><th>Cận dưới tham khảo</th><th>Cận trên tham khảo</th><th>Cảnh báo</th></tr></thead><tbody>{current.values.map(p=><tr key={p.id}><td>{p.forecastDate.slice(0,10)}</td><td>{Number(p.value).toFixed(2)}</td><td>{Number(p.lower).toFixed(2)}</td><td>{Number(p.upper).toFixed(2)}</td><td>{p.warning?'Vượt ngưỡng':'—'}</td></tr>)}</tbody></table></div><p>Điểm bất thường theo phần dư: {current.anomalies.length}</p><p className="muted">{current.limitations}</p></section>}
 <section className="card"><h2>Lịch sử dự báo</h2>{runs.length===0?<p>Chưa có kết quả</p>:runs.map(r=><p key={r.id}><button type="button" onClick={()=>setCurrent(r)}>{r.kpiCode} · {new Date(r.createdAt).toLocaleString('vi-VN')} · {r.horizon??r.values.length} ngày</button></p>)}</section>
 </main>;
}
