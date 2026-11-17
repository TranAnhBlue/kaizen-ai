import { BadGatewayException, BadRequestException, Body, Controller, ForbiddenException, Get, NotFoundException, Param, Post, Req, UseGuards } from '@nestjs/common';
import { IsString, IsUUID, MaxLength, MinLength, IsOptional } from 'class-validator';
import type { Request } from 'express';
import { PrismaService } from '../../database/prisma.service';
import { JwtGuard, Principal } from '../../common/guards/jwt.guard';

type AuthReq = Request & { principal: Principal };
class AskDto {
 @IsString() @MinLength(2) @MaxLength(2000) question!: string;
 @IsOptional() @IsUUID() conversationId?: string;
}
class UploadDto {
 @IsString() @MinLength(2) @MaxLength(200) title!: string;
 @IsString() @MaxLength(100) mimeType!: string;
 @IsString() @MinLength(4) @MaxLength(7500000) contentBase64!: string;
}
async function callAi(path: string, payload: unknown) {
 const url = process.env.AI_SERVICE_URL;
 const token = process.env.AI_SERVICE_TOKEN;
 if (!url || !token) throw new BadGatewayException('AI service not configured');
 try {
  const response = await fetch(`${url.replace(/\/$/,'')}/internal/rag/${path}`, { method:'POST', headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`}, body:JSON.stringify(payload), signal:AbortSignal.timeout(45000) });
  if (!response.ok) throw new Error(`AI service HTTP ${response.status}`);
  return await response.json() as any;
 } catch { throw new BadGatewayException('AI service unavailable or document invalid'); }
}
@Controller('ai-chat') @UseGuards(JwtGuard)
export class AiChatController {
 constructor(private readonly db: PrismaService) {}
 @Get('documents') documents(@Req() req:AuthReq) {
  return this.db.document.findMany({where:{tenantId:req.principal.tenantId},select:{id:true,title:true,mimeType:true,createdAt:true,status:true},orderBy:{createdAt:'desc'},take:100});
 }
 @Post('documents') async upload(@Req() req:AuthReq,@Body() dto:UploadDto) {
  if (req.principal.role==='EMPLOYEE') throw new ForbiddenException('Manager role required');
  if (!['text/plain','application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(dto.mimeType)) throw new BadRequestException('Only TXT, PDF, DOCX supported');
  if (!/^[A-Za-z0-9+/]*={0,2}$/.test(dto.contentBase64) || dto.contentBase64.length%4!==0 || Buffer.byteLength(dto.contentBase64,'base64')>5*1024*1024) throw new BadRequestException('Invalid or oversized file');
  const parsed = await callAi('extract',{mime_type:dto.mimeType,content_base64:dto.contentBase64});
  if (!Array.isArray(parsed.chunks) || parsed.chunks.length===0 || parsed.chunks.length>400) throw new BadRequestException('No extractable text');
  const tenantId=req.principal.tenantId;
  const result = await this.db.$transaction(async tx=>{
   const doc=await tx.document.create({data:{tenantId,title:dto.title,storageKey:`db-chunks:${crypto.randomUUID()}`,mimeType:dto.mimeType,uploadedById:req.principal.sub}});
   await tx.documentChunk.createMany({data:parsed.chunks.map((content:string)=>({tenantId,documentId:doc.id,content}))});
   return {id:doc.id,title:doc.title,chunks:parsed.chunks.length,truncated:!!parsed.truncated};
  });
  // Optional embedding enrichment: documents remain usable via lexical retrieval if provider unavailable.
  if (process.env.EMBEDDING_ENABLED === 'true') {
   const saved = await this.db.documentChunk.findMany({where:{tenantId,documentId:result.id},select:{id:true,content:true}});
   for (let offset=0;offset<saved.length;offset+=16) {
    const batch=saved.slice(offset,offset+16);
    const response=await callAi('embed',{texts:batch.map(x=>x.content)});
    if (!Array.isArray(response.vectors) || response.vectors.length!==batch.length) throw new BadGatewayException('Invalid embeddings');
    for (let i=0;i<batch.length;i++) {
     const vector=response.vectors[i];
     if (!Array.isArray(vector) || vector.length!==1536 || !vector.every((v:unknown)=>typeof v==='number' && Number.isFinite(v))) throw new BadGatewayException('Invalid embedding dimensions');
     await this.db.$executeRaw`UPDATE "document_chunks" SET "embedding" = ${'['+vector.join(',')+']'}::vector WHERE "id" = ${batch[i].id}::uuid AND "tenantId" = ${tenantId}::uuid`;
    }
   }
  }
  return result;
 }
 @Get('conversations') conversations(@Req() req:AuthReq) {
  return this.db.aiConversation.findMany({where:{tenantId:req.principal.tenantId,userId:req.principal.sub},orderBy:{createdAt:'desc'},take:50});
 }
 @Get('conversations/:id') async history(@Req() req:AuthReq,@Param('id') id:string) {
  const conversation=await this.db.aiConversation.findFirst({where:{id,tenantId:req.principal.tenantId,userId:req.principal.sub},include:{messages:{orderBy:{createdAt:'asc'},take:100}}});
  if (!conversation) throw new NotFoundException();
  return conversation;
 }
 @Post('ask') async ask(@Req() req:AuthReq,@Body() dto:AskDto) {
  const tenantId=req.principal.tenantId;
  let conversation = dto.conversationId ? await this.db.aiConversation.findFirst({where:{id:dto.conversationId,tenantId,userId:req.principal.sub}}) : null;
  if (dto.conversationId && !conversation) throw new NotFoundException('Conversation not found');
  // Tenant scope is applied before any text can be sent to the AI service.
  let vectorEvidence: {id:string;documentId:string;content:string;title:string}[] = [];
  if (process.env.EMBEDDING_ENABLED === 'true') {
   const embedded=await callAi('embed',{texts:[dto.question]});
   const vector=embedded.vectors?.[0];
   if (!Array.isArray(vector) || vector.length!==1536 || !vector.every((v:unknown)=>typeof v==='number' && Number.isFinite(v))) throw new BadGatewayException('Invalid query embedding');
   vectorEvidence=await this.db.$queryRaw<{id:string;documentId:string;content:string;title:string}[]>`
     SELECT c."id",c."documentId",c."content",d."title"
     FROM "document_chunks" c JOIN "documents" d ON d."id"=c."documentId" AND d."tenantId"=c."tenantId"
     WHERE c."tenantId"=${tenantId}::uuid AND c."embedding" IS NOT NULL AND d."status"='READY'
     ORDER BY c."embedding" <=> ${'['+vector.join(',')+']'}::vector LIMIT 6`;
  }
  const tokens = Array.from(new Set((dto.question.toLowerCase().match(/[\p{L}\p{N}]{3,}/gu)??[]))).slice(0,12);
  const chunks = tokens.length ? await this.db.documentChunk.findMany({where:{tenantId,OR:tokens.map(t=>({content:{contains:t,mode:'insensitive'}}))},include:{document:{select:{title:true}}},take:150}) : [];
  const ranked=chunks.map(c=>({...c,score:tokens.reduce((n,t)=>n+(c.content.toLowerCase().includes(t)?1:0),0)})).sort((a,b)=>b.score-a.score).slice(0,6);
  const evidence=vectorEvidence.length ? vectorEvidence.map(c=>({chunk_id:c.id,document_id:c.documentId,title:c.title,content:c.content})) : ranked.map(c=>({chunk_id:c.id,document_id:c.documentId,title:c.document.title,content:c.content}));
  const answer=await callAi('answer',{question:dto.question,evidence});
  if (!conversation) conversation=await this.db.aiConversation.create({data:{tenantId,userId:req.principal.sub,title:dto.question.slice(0,180)}});
  const citations=evidence.map((e,i)=>({number:i+1,documentId:e.document_id,chunkId:e.chunk_id,title:e.title,excerpt:e.content.slice(0,200)}));
  await this.db.aiMessage.createMany({data:[{tenantId,conversationId:conversation.id,role:'user',content:dto.question},{tenantId,conversationId:conversation.id,role:'assistant',content:String(answer.answer).slice(0,8000),citations}]});
  return {conversationId:conversation.id,answer:answer.answer,mode:answer.mode,citations};
 }
}
