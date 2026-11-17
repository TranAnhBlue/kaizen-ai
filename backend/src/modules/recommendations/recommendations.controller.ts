import { BadGatewayException, BadRequestException, Body, ConflictException, Controller, ForbiddenException, Get, Param, ParseUUIDPipe, Patch, Post, Req, UseGuards } from '@nestjs/common';
import { IsEnum, IsOptional, IsString, IsUUID, MaxLength } from 'class-validator';
import type { Request } from 'express';
import { PrismaService } from '../../database/prisma.service';
import { JwtGuard, Principal } from '../../common/guards/jwt.guard';
import { randomUUID } from 'crypto';
type AuthReq = Request & {principal:Principal};
class GenerateDto { @IsUUID() forecastRunId!:string; }
class ReviewDto { @IsEnum(['APPROVED','REJECTED','IMPLEMENTED']) status!: 'APPROVED'|'REJECTED'|'IMPLEMENTED'; @IsOptional() @IsString() @MaxLength(2000) note?:string; }
@Controller('recommendations') @UseGuards(JwtGuard)
export class RecommendationsController {
 constructor(private readonly db:PrismaService){}
 @Get() list(@Req() req:AuthReq){return this.db.aiRecommendation.findMany({where:{tenantId:req.principal.tenantId},orderBy:{createdAt:'desc'},take:100,include:{events:{orderBy:{createdAt:'asc'}}}});}
 @Get(':id') async detail(@Req() req:AuthReq,@Param('id',ParseUUIDPipe) id:string){const item=await this.db.aiRecommendation.findFirst({where:{id,tenantId:req.principal.tenantId},include:{events:{orderBy:{createdAt:'asc'}}}});if(!item)throw new BadRequestException('Recommendation not found');return item;}
 @Post('generate') async generate(@Req() req:AuthReq,@Body() dto:GenerateDto){
  if(req.principal.role==='EMPLOYEE')throw new ForbiddenException('Manager required');
  const tenantId=req.principal.tenantId;
  const run=await this.db.forecastRun.findFirst({where:{id:dto.forecastRunId,tenantId},include:{values:{orderBy:{forecastDate:'asc'}}}});
  if(!run)throw new BadRequestException('Forecast run not found');
  const kpi=await this.db.kpiDefinition.findUnique({where:{tenantId_code:{tenantId,code:run.kpiCode}}});
  if(!kpi)throw new BadRequestException('KPI not found');
  // Idempotency: one recommendation per forecast run and tenant.
  const existing=await this.db.aiRecommendation.findFirst({where:{tenantId,forecastRunId:run.id}});
  if(existing)throw new ConflictException('Recommendation already generated for this run');
  const url=process.env.AI_SERVICE_URL,token=process.env.AI_SERVICE_TOKEN;
  if(!url||!token)throw new BadGatewayException('AI service is not configured');
  let proposals:any[];
  try {
   const response=await fetch(`${url.replace(/\/$/,'')}/internal/recommendations/generate`,{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},body:JSON.stringify({kpi:{code:kpi.code,direction:kpi.direction,target:kpi.target===null?null:Number(kpi.target)},run:{id:run.id,model:run.model,values:run.values.map(v=>({date:v.forecastDate.toISOString().slice(0,10),value:Number(v.value),warning:v.warning}))}}),signal:AbortSignal.timeout(15000)});
   if(!response.ok)throw new Error('AI service error');
   const payload=await response.json() as {recommendations?:any[]};
   if(!Array.isArray(payload.recommendations))throw new Error('Invalid response');
   proposals=payload.recommendations.slice(0,3);
  }catch{throw new BadGatewayException('Recommendation service unavailable');}
  const created=[];
  for(const p of proposals){
   if(typeof p.title!=='string'||typeof p.rationale!=='string'||typeof p.suggested_action!=='string'||!['LOW','MEDIUM','HIGH'].includes(p.priority)||!p.evidence||typeof p.limitations!=='string')throw new BadGatewayException('Invalid recommendation');
   const item=await this.db.aiRecommendation.create({data:{id:randomUUID(),tenantId,forecastRunId:run.id,kpiCode:run.kpiCode,createdById:req.principal.sub,title:p.title.slice(0,200),rationale:p.rationale,suggestedAction:p.suggested_action,priority:p.priority,evidence:p.evidence,limitations:p.limitations,events:{create:{id:randomUUID(),tenantId,actorId:req.principal.sub,action:'GENERATED',toStatus:'PROPOSED'}}}}});created.push(item);
  }
  return created;
 }
 @Patch(':id/review') async review(@Req() req:AuthReq,@Param('id',ParseUUIDPipe) id:string,@Body() dto:ReviewDto){
  if(req.principal.role==='EMPLOYEE')throw new ForbiddenException('Manager required');
  const tenantId=req.principal.tenantId;
  return this.db.$transaction(async tx=>{
   const item=await tx.aiRecommendation.findFirst({where:{id,tenantId}});
   if(!item)throw new BadRequestException('Recommendation not found');
   if(item.createdById===req.principal.sub && dto.status!=='IMPLEMENTED')throw new ForbiddenException('Creator cannot approve or reject own recommendation');
   const allowed=(item.status==='PROPOSED'&&['APPROVED','REJECTED'].includes(dto.status))||(item.status==='APPROVED'&&dto.status==='IMPLEMENTED');
   if(!allowed)throw new ConflictException('Invalid recommendation transition');
   if(dto.status==='REJECTED'&&!dto.note?.trim())throw new BadRequestException('Rejection reason required');
   const changed=await tx.aiRecommendation.updateMany({where:{id,tenantId,status:item.status},data:{status:dto.status,reviewedById:req.principal.sub,reviewedAt:new Date(),...(dto.status==='IMPLEMENTED'?{outcomeNote:dto.note??null}:{reviewNote:dto.note??null})}});
   if(changed.count!==1)throw new ConflictException('Recommendation was changed by another user');
   await tx.recommendationEvent.create({data:{id:randomUUID(),recommendationId:id,tenantId,actorId:req.principal.sub,action:dto.status,fromStatus:item.status,toStatus:dto.status,note:dto.note}});
   return tx.aiRecommendation.findUnique({where:{id},include:{events:{orderBy:{createdAt:'asc'}}}});
  });
 }
}
