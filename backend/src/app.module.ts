import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { HealthController } from './health/health.controller';
import { PrismaModule } from './database/prisma.module';
import { KaizenModule } from './modules/kaizen/kaizen.module';
@Module({ imports: [ConfigModule.forRoot({ isGlobal: true }), PrismaModule, KaizenModule], controllers: [HealthController] })
export class AppModule {}
