import { Module } from '@nestjs/common';
import { KaizenController } from './kaizen.controller';
import { KaizenService } from './kaizen.service';
@Module({ controllers: [KaizenController], providers: [KaizenService] }) export class KaizenModule {}
