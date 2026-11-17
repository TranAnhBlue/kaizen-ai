import { CanActivate, ExecutionContext, ForbiddenException, Injectable, SetMetadata } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import type { Request } from 'express';
import { Principal } from './jwt.guard';
export const ROLES_KEY = 'kaizen_roles';
export const Roles = (...roles: Principal['role'][]) => SetMetadata(ROLES_KEY, roles);
@Injectable() export class RolesGuard implements CanActivate {
 constructor(private readonly reflector: Reflector) {}
 canActivate(context: ExecutionContext): boolean {
  const roles = this.reflector.getAllAndOverride<Principal['role'][]>(ROLES_KEY,[context.getHandler(),context.getClass()]);
  if (!roles?.length) return true;
  const req = context.switchToHttp().getRequest<Request & {principal?:Principal}>();
  if (!req.principal || !roles.includes(req.principal.role)) throw new ForbiddenException('Insufficient permissions');
  return true;
 }
}
