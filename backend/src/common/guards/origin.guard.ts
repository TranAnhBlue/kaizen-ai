import { CanActivate, ExecutionContext, ForbiddenException, Injectable } from '@nestjs/common';
import type { Request } from 'express';
@Injectable() export class OriginGuard implements CanActivate {
 canActivate(ctx: ExecutionContext): boolean {
  const req = ctx.switchToHttp().getRequest<Request>();
  if (['GET','HEAD','OPTIONS'].includes(req.method)) return true;
  const allowed = (process.env.CORS_ORIGIN ?? 'http://localhost:3000').split(',').map(s=>s.trim());
  const origin = req.headers.origin;
  if (!origin || !allowed.includes(origin)) throw new ForbiddenException('Untrusted request origin');
  return true;
 }
}
