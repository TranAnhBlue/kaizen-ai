import { Module } from '@nestjs/common';
import { ForecastingController } from './forecasting.controller';
@Module({controllers:[ForecastingController]})
export class ForecastingModule {}
