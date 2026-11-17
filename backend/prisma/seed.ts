import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { hash } from 'bcryptjs';
async function main() {
 const email = process.env.SEED_ADMIN_EMAIL?.trim().toLowerCase();
 const password = process.env.SEED_ADMIN_PASSWORD;
 const name = process.env.SEED_TENANT_NAME?.trim();
 if (!email || !password || password.length < 12 || !name) throw new Error('Set SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD (12+ chars), SEED_TENANT_NAME');
 const db = new PrismaClient();
 try {
  if (await db.user.findFirst({ where: { email } })) throw new Error('Email already exists; seed will not overwrite accounts');
  await db.tenant.create({ data: { name, users: { create: { email, passwordHash: await hash(password, 12), fullName: 'Administrator', role: 'TENANT_ADMIN' } } } });
  console.log('Tenant and admin created');
 } finally { await db.$disconnect(); }
}
main().catch(e=>{ console.error(e.message); process.exitCode=1; });
