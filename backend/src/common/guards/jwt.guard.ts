import { CanActivate, ExecutionContext, Injectable, UnauthorizedException } from '@nestjs/common';
import { verify, JwtPayload } from 'jsonwebtoken';
import type { Request } from 'express';
export interface Principal { sub: string; tenantId: string; role: 'TENANT_ADMIN'|'MANAGER'|'EMPLOYEE'; }
@Injectable() export class JwtGuard implements CanActivate {
 canActivate(ctx: ExecutionContext): boolean {
  const req = ctx.switchToHttp().getRequest<Request & { principal?: Principal }>();
  const token = req.cookies?.kaizen_session;
  if (!token || typeof token !== 'string') throw new UnauthorizedException();
  try {
   const secret = process.env.JWT_SECRET;
   if (!secret) throw new Error('Missing secret');
   const payload = verify(token, secret, { issuer: 'kaizen-api', audience: 'kaizen-web', algorithms: ['HS256'] }) as JwtPayload;
   if (typeof payload.sub !== 'string' || typeof payload.tenantId !== 'string' || !['TENANT_ADMIN','MANAGER','EMPLOYEE'].includes(payload.role)) throw new Error('Invalid claims');
   req.principal = { sub: payload.sub, tenantId: payload.tenantId, role: payload.role } as Principal;
   return true;
  } catch { throw new UnauthorizedException('Invalid or expired session'); }
 }
}
