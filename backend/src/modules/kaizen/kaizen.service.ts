import { BadRequestException, ConflictException, ForbiddenException, Injectable, NotFoundException } from '@nestjs/common';
import { Prisma, KaizenStatus } from '@prisma/client';
import { PrismaService } from '../../database/prisma.service';
import { Principal } from '../../common/guards/jwt.guard';
import { CreateKaizenDto } from './dto/create-kaizen.dto';
import { TransitionKaizenDto } from './dto/transition-kaizen.dto';
const transitions: Record<TransitionKaizenDto['action'], {from: KaizenStatus; to: KaizenStatus; roles: Principal['role'][]}> = {
 SUBMIT:{from:'DRAFT',to:'SUBMITTED',roles:['EMPLOYEE','MANAGER','TENANT_ADMIN']},
 APPROVE:{from:'SUBMITTED',to:'APPROVED',roles:['MANAGER','TENANT_ADMIN']},
 REJECT:{from:'SUBMITTED',to:'REJECTED',roles:['MANAGER','TENANT_ADMIN']},
 START:{from:'APPROVED',to:'IN_PROGRESS',roles:['MANAGER','TENANT_ADMIN']},
 COMPLETE:{from:'IN_PROGRESS',to:'COMPLETED',roles:['MANAGER','TENANT_ADMIN']},
 REOPEN:{from:'REJECTED',to:'DRAFT',roles:['MANAGER','TENANT_ADMIN']}
};
@Injectable() export class KaizenService {
 constructor(private readonly db: PrismaService) {}
 list(tenantId:string) { return this.db.kaizenProject.findMany({where:{tenantId},orderBy:{createdAt:'desc'}}); }
 async detail(tenantId:string,id:string){
  const project=await this.db.kaizenProject.findFirst({where:{tenantId,id},include:{auditEvents:{orderBy:{createdAt:'desc'}}}});
  if(!project) throw new NotFoundException('Kaizen not found');
  return project;
 }
 create(principal:Principal,dto:CreateKaizenDto){return this.db.kaizenProject.create({data:{tenantId:principal.tenantId,createdById:principal.sub,title:dto.title,description:dto.description}});}
 async transition(principal:Principal,id:string,dto:TransitionKaizenDto){
  const rule=transitions[dto.action];
  if(!rule) throw new BadRequestException('Unknown action');
  if(!rule.roles.includes(principal.role)) throw new ForbiddenException('Action not permitted for this role');
  if(dto.action==='REJECT' && !dto.comment?.trim()) throw new BadRequestException('Rejection reason is required');
  return this.db.$transaction(async tx=>{
   const current=await tx.kaizenProject.findFirst({where:{id,tenantId:principal.tenantId}});
   if(!current) throw new NotFoundException('Kaizen not found');
   if(current.status!==rule.from) throw new ConflictException(`Expected ${rule.from}, received ${current.status}`);
   if(dto.action==='SUBMIT' && current.createdById && current.createdById!==principal.sub && principal.role==='EMPLOYEE') throw new ForbiddenException('Cannot submit another employee project');
   if(['APPROVE','REJECT'].includes(dto.action) && current.createdById===principal.sub) throw new ForbiddenException('Self-approval is not allowed');
   const data: Prisma.KaizenProjectUpdateManyMutationInput={status:rule.to};
   if(dto.action==='SUBMIT') data.submittedAt=new Date();
   if(['APPROVE','REJECT'].includes(dto.action)){data.reviewedAt=new Date();data.reviewedById=principal.sub;}
   if(dto.action==='REOPEN'){data.reviewedAt=null;data.reviewedById=null;}
   const changed=await tx.kaizenProject.updateMany({where:{id,tenantId:principal.tenantId,status:rule.from},data});
   if(changed.count!==1) throw new ConflictException('Status changed concurrently');
   await tx.kaizenAuditEvent.create({data:{tenantId:principal.tenantId,projectId:id,actorId:principal.sub,action:dto.action,fromStatus:rule.from,toStatus:rule.to,comment:dto.comment?.trim()||null}});
   return tx.kaizenProject.findFirstOrThrow({where:{id,tenantId:principal.tenantId}});
  });
 }
}
