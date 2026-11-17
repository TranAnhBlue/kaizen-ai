import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PrismaService } from '../../database/prisma.service';
import { compare } from 'bcryptjs';
import { sign } from 'jsonwebtoken';
@Injectable() export class AuthService {
 constructor(private readonly db: PrismaService) {}
 async login(email: string, password: string) {
  const user = await this.db.user.findFirst({ where: { email: email.toLowerCase().trim() } });
  if (!user || !(await compare(password, user.passwordHash))) throw new UnauthorizedException('Invalid credentials');
  const secret = process.env.JWT_SECRET;
  if (!secret || secret.length < 32) throw new Error('JWT_SECRET must contain at least 32 characters');
  const token = sign({ sub: user.id, tenantId: user.tenantId, role: user.role }, secret, { expiresIn: '30m', issuer: 'kaizen-api', audience: 'kaizen-web' });
  return { token, user: { id: user.id, email: user.email, fullName: user.fullName, role: user.role, tenantId: user.tenantId } };
 }
}
