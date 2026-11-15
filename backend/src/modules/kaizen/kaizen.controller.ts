import { Body, Controller, ForbiddenException, Get, Post, Query } from '@nestjs/common';
import { KaizenService } from './kaizen.service';
import { CreateKaizenDto } from './dto/create-kaizen.dto';
@Controller('kaizen') export class KaizenController {
 constructor(private readonly service: KaizenService) {}
 private ensureDemo() { if (process.env.ENABLE_DEMO_ROUTES !== 'true' || process.env.NODE_ENV === 'production') throw new ForbiddenException('Demo endpoints disabled'); }
 @Get() list(@Query('tenantId') tenantId: string) { this.ensureDemo(); return this.service.list(tenantId); }
 @Post() create(@Body() dto: CreateKaizenDto) { this.ensureDemo(); return this.service.create(dto); }
}
