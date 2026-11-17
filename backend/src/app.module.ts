import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerGuard, ThrottlerModule } from '@nestjs/throttler';
import { ConfigModule } from '@nestjs/config';
import { HealthController } from './health/health.controller';
import { PrismaModule } from './database/prisma.module';
import { KaizenModule } from './modules/kaizen/kaizen.module';
import { KpiModule } from './modules/kpi/kpi.module';
import { AuthModule } from './modules/auth/auth.module';
import { AiChatModule } from './modules/ai-chat/ai-chat.module';
import { RecommendationsModule } from './modules/recommendations/recommendations.module';
import { ForecastingModule } from './modules/forecasting/forecasting.module';
import { OriginGuard } from './common/guards/origin.guard';
@Module({ imports: [ConfigModule.forRoot({ isGlobal: true }), ThrottlerModule.forRoot([{ ttl: 60000, limit: 30 }]), PrismaModule, AuthModule, KaizenModule, KpiModule, AiChatModule, ForecastingModule, RecommendationsModule], controllers: [HealthController], providers: [{ provide: APP_GUARD, useClass: OriginGuard }, { provide: APP_GUARD, useClass: ThrottlerGuard }] })
export class AppModule {}
