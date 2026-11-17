import { BadGatewayException, BadRequestException, Body, Controller, ForbiddenException, Get, Param, Post, Query, Req, UseGuards } from '@nestjs/common';
import { IsInt, IsString, Max, MaxLength, Min } from 'class-validator';
import type { Request } from 'express';
import { PrismaService } from '../../database/prisma.service';
import { JwtGuard, Principal } from '../../common/guards/jwt.guard';

type AuthReq = Request & { principal: Principal };
class ForecastDto {
 @IsString() @MaxLength(60) code!: string;
 @IsInt() @Min(1) @Max(30) horizon!: number;
}
@Controller('forecasting') @UseGuards(JwtGuard)
export class ForecastingController {
 constructor(private readonly db: PrismaService) {}
 @Get('runs') list(@Req() req:AuthReq,@Query('code') code?:string) {
  return this.db.forecastRun.findMany({where:{tenantId:req.principal.tenantId,...(code?{kpiCode:code}:{})},orderBy:{createdAt:'desc'},take:50,include:{values:{orderBy:{forecastDate:'asc'}}}});
 }
 @Get('runs/:id') async detail(@Req() req:AuthReq,@Param('id') id:string) {
  if (!/^[0-9a-f-]{36}$/i.test(id)) throw new BadRequestException('Invalid run id');
  const run=await this.db.forecastRun.findFirst({where:{id,tenantId:req.principal.tenantId},include:{values:{orderBy:{forecastDate:'asc'}}}});
  if(!run) throw new BadRequestException('Forecast run not found');
  return run;
 }
 @Post('predict') async predict(@Req() req:AuthReq,@Body() dto:ForecastDto) {
  if(req.principal.role==='EMPLOYEE') throw new ForbiddenException('Manager role required');
  const tenantId=req.principal.tenantId;
  const def=await this.db.kpiDefinition.findUnique({where:{tenantId_code:{tenantId,code:dto.code}}});
  if(!def) throw new BadRequestException('KPI definition not found');
  const records=await this.db.kpiRecord.findMany({where:{tenantId,metric:dto.code},orderBy:[{recordedAt:'desc'},{id:'desc'}],take:1000});
  // Aggregate multiple observations per UTC day by mean. Missing dates are rejected by the AI service.
  const daily=new Map<string,{sum:number,count:number}>();
  for(const r of records){const date=r.recordedAt.toISOString().slice(0,10);const item=daily.get(date)??{sum:0,count:0};item.sum+=Number(r.value);item.count++;daily.set(date,item);}
  const observations=[...daily.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([date,x])=>({date,value:x.sum/x.count}));
  if(observations.length<8) throw new BadRequestException('At least 8 distinct daily KPI values are required');
  const url=process.env.AI_SERVICE_URL, token=process.env.AI_SERVICE_TOKEN;
  if(!url||!token) throw new BadGatewayException('AI service is not configured');
  let result:any;
  try {
   const response=await fetch(`${url.replace(/\/$/,'')}/internal/forecasting/predict`,{
    method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},
    body:JSON.stringify({observations,horizon:dto.horizon,warning_min:def.warningMin===null?null:Number(def.warningMin),warning_max:def.warningMax===null?null:Number(def.warningMax)}),signal:AbortSignal.timeout(20000)});
   if(response.status===422){const detail=await response.json() as {detail?:string};throw new BadRequestException(detail.detail??'Invalid time series');}
   if(!response.ok) throw new Error(`AI HTTP ${response.status}`);
   result=await response.json();
  } catch(e){if(e instanceof BadRequestException)throw e;throw new BadGatewayException('Forecast service unavailable');}
  if(!Array.isArray(result.forecast)||result.forecast.length!==dto.horizon)throw new BadGatewayException('Invalid forecast response');
  return this.db.forecastRun.create({data:{tenantId,requestedById:req.principal.sub,kpiCode:dto.code,horizon:dto.horizon,model:result.model,trainingPoints:result.training_points,holdoutPoints:result.holdout_points,metrics:result.metrics,anomalies:result.anomalies,limitations:result.limitations,values:{create:result.forecast.map((p:any)=>({forecastDate:new Date(`${p.date}T00:00:00Z`),value:p.value,lower:p.lower,upper:p.upper,warning:p.warning}))}},include:{values:{orderBy:{forecastDate:'asc'}}}});
 }
}
