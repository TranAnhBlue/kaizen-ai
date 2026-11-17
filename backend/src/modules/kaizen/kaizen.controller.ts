import { Body, Controller, Get, Param, ParseUUIDPipe, Patch, Post, Req, UseGuards } from '@nestjs/common';
import type { Request } from 'express';
import { KaizenService } from './kaizen.service';
import { CreateKaizenDto } from './dto/create-kaizen.dto';
import { TransitionKaizenDto } from './dto/transition-kaizen.dto';
import { JwtGuard, Principal } from '../../common/guards/jwt.guard';
import { Roles, RolesGuard } from '../../common/guards/roles.guard';
type AuthRequest = Request & {principal:Principal};
@Controller('kaizen') @UseGuards(JwtGuard,RolesGuard) export class KaizenController {
 constructor(private readonly service:KaizenService){}
 @Get() list(@Req() req:AuthRequest){return this.service.list(req.principal.tenantId);}
 @Get(':id') detail(@Req() req:AuthRequest,@Param('id',ParseUUIDPipe) id:string){return this.service.detail(req.principal.tenantId,id);}
 @Post() @Roles('EMPLOYEE','MANAGER','TENANT_ADMIN') create(@Req() req:AuthRequest,@Body() dto:CreateKaizenDto){return this.service.create(req.principal,dto);}
 @Patch(':id/transition') transition(@Req() req:AuthRequest,@Param('id',ParseUUIDPipe) id:string,@Body() dto:TransitionKaizenDto){return this.service.transition(req.principal,id,dto);}
}
