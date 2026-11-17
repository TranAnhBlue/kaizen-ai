import { BadRequestException, Body, Controller, Get, Post, Query, Req, UseGuards, ForbiddenException } from '@nestjs/common';
import type { Request } from 'express';
import { PrismaService } from '../../database/prisma.service';
import { JwtGuard, Principal } from '../../common/guards/jwt.guard';
import { CreateKpiDto } from './dto/create-kpi.dto';
import { CreateKpiDefinitionDto } from './dto/kpi-definition.dto';

type AuthReq = Request & { principal: Principal };
@Controller('kpi') @UseGuards(JwtGuard)
export class KpiController {
 constructor(private readonly db: PrismaService) {}
 private canManage(req: AuthReq) { if (req.principal.role === 'EMPLOYEE') throw new ForbiddenException('Manager role required'); }
 @Get() list(@Req() req: AuthReq) {
  return this.db.kpiRecord.findMany({ where: { tenantId: req.principal.tenantId }, orderBy: { recordedAt: 'desc' }, take: 200 });
 }
 @Post() async create(@Req() req: AuthReq, @Body() dto: CreateKpiDto) {
  this.canManage(req);
  const def = await this.db.kpiDefinition.findUnique({where:{tenantId_code:{tenantId:req.principal.tenantId,code:dto.metric}}});
  if (!def) throw new BadRequestException('Create KPI definition before adding measurements');
  if (def.unit !== dto.unit) throw new BadRequestException('Unit does not match KPI definition');
  return this.db.kpiRecord.create({ data: { tenantId: req.principal.tenantId, metric: dto.metric, value: dto.value, unit: dto.unit, recordedAt: new Date(dto.recordedAt) } });
 }
 @Get('definitions') definitions(@Req() req: AuthReq) {
  return this.db.kpiDefinition.findMany({where:{tenantId:req.principal.tenantId},orderBy:{name:'asc'}});
 }
 @Post('definitions') async define(@Req() req: AuthReq,@Body() dto: CreateKpiDefinitionDto) {
  this.canManage(req);
  if(dto.warningMin != null && dto.warningMax != null && dto.warningMin > dto.warningMax) throw new BadRequestException('warningMin must be <= warningMax');
  const existing=await this.db.kpiDefinition.findUnique({where:{tenantId_code:{tenantId:req.principal.tenantId,code:dto.code}}});
  if(existing) throw new BadRequestException('KPI code already exists');
  return this.db.kpiDefinition.create({data:{tenantId:req.principal.tenantId,...dto}});
 }
 @Get('analytics') async analytics(@Req() req: AuthReq,@Query('code') code?: string) {
  const defs=await this.db.kpiDefinition.findMany({where:{tenantId:req.principal.tenantId,...(code?{code}:{})}});
  const records=await this.db.kpiRecord.findMany({where:{tenantId:req.principal.tenantId,...(code?{metric:code}:{})},orderBy:{recordedAt:'asc'},take:5000});
  return defs.map(d=>{
   const rows=records.filter(r=>r.metric===d.code);
   const values=rows.map(r=>Number(r.value));
   const average=values.length?values.reduce((a,b)=>a+b,0)/values.length:null;
   const latest=rows.at(-1);
   const violations=rows.filter(r=>(d.warningMin!==null&&Number(r.value)<Number(d.warningMin))||(d.warningMax!==null&&Number(r.value)>Number(d.warningMax)));
   return {definition:d,count:rows.length,average,latest:latest?{value:Number(latest.value),recordedAt:latest.recordedAt}:null,violations:violations.length,series:rows.slice(-90).map(r=>({date:r.recordedAt,value:Number(r.value),alert:(d.warningMin!==null&&Number(r.value)<Number(d.warningMin))||(d.warningMax!==null&&Number(r.value)>Number(d.warningMax))}))};
  });
 }
 @Post('import-csv') async importCsv(@Req() req: AuthReq,@Body() body: {csv?:string}) {
  this.canManage(req);
  if(typeof body?.csv!=='string'||Buffer.byteLength(body.csv,'utf8')>1024*1024) throw new BadRequestException('CSV must be text <= 1 MB');
  const lines=body.csv.replace(/^\uFEFF/,'').trim().split(/\r?\n/);
  if(lines.length<2||lines.length>501||lines[0].trim()!=='code,value,recordedAt') throw new BadRequestException('CSV header must be code,value,recordedAt (max 500 rows)');
  const defs=await this.db.kpiDefinition.findMany({where:{tenantId:req.principal.tenantId}});
  const map=new Map(defs.map(d=>[d.code,d]));
  const rows=lines.slice(1).map((line,i)=>{
   // Strict unquoted numeric CSV format; reject complex CSV instead of silently misparsing.
   const fields=line.split(',');if(fields.length!==3) throw new BadRequestException(`Row ${i+2}: invalid columns`);
   const [code,raw,date]=fields.map(x=>x.trim());const def=map.get(code);
   if(!def) throw new BadRequestException(`Row ${i+2}: unknown KPI code`);
   if(!/^-?\d+(\.\d{1,4})?$/.test(raw)||!Number.isFinite(Number(raw))) throw new BadRequestException(`Row ${i+2}: invalid value`);
   if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||Number.isNaN(Date.parse(date))||new Date(date).toISOString().slice(0,10)!==date) throw new BadRequestException(`Row ${i+2}: invalid date`);
   return {tenantId:req.principal.tenantId,metric:code,value:Number(raw),unit:def.unit,recordedAt:new Date(`${date}T12:00:00Z`)};
  });
  const result=await this.db.kpiRecord.createMany({data:rows});return {imported:result.count};
 }
}
