import { Body, Controller, Get, Post, Req, Res, UseGuards } from '@nestjs/common';
import type { Request, Response } from 'express';
import { AuthService } from './auth.service';
import { LoginDto } from './dto/login.dto';
import { JwtGuard, Principal } from '../../common/guards/jwt.guard';
@Controller('auth') export class AuthController {
 constructor(private readonly auth: AuthService) {}
 @Post('login') async login(@Body() dto: LoginDto, @Res({ passthrough: true }) res: Response) {
  const result = await this.auth.login(dto.email, dto.password);
  res.cookie('kaizen_session', result.token, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax', path: '/api/v1', maxAge: 30*60*1000 });
  return { user: result.user };
 }
 @UseGuards(JwtGuard) @Get('me') me(@Req() req: Request & { principal: Principal }) { return req.principal; }
 @Post('logout') logout(@Res({ passthrough: true }) res: Response) {
  res.clearCookie('kaizen_session', { path: '/api/v1', sameSite: 'lax', secure: process.env.NODE_ENV === 'production' });
  return { success: true };
 }
}
