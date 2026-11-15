import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../database/prisma.service';
import { CreateKaizenDto } from './dto/create-kaizen.dto';
@Injectable() export class KaizenService {
 constructor(private readonly db: PrismaService) {}
 list(tenantId: string) { return this.db.kaizenProject.findMany({ where: { tenantId }, orderBy: { createdAt: 'desc' } }); }
 create(dto: CreateKaizenDto) { return this.db.kaizenProject.create({ data: { tenantId: dto.tenantId, title: dto.title, description: dto.description } }); }
}
