import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { hash } from 'bcryptjs';

/** Explicitly opt-in demo data; never run against production. Aborts safely if the demo admin email already exists. */
async function main() {
  if (process.env.NODE_ENV === 'production' || process.env.ALLOW_DEMO_SEED !== 'true') {
    throw new Error('Demo seed blocked: set ALLOW_DEMO_SEED=true in a non-production environment');
  }
  const name = process.env.DEMO_TENANT_NAME || 'Kaizen Demo Organization';
  const adminEmail = process.env.DEMO_ADMIN_EMAIL?.trim().toLowerCase();
  const adminPassword = process.env.DEMO_ADMIN_PASSWORD;
  if (!adminEmail || !adminPassword || adminPassword.length < 12) {
    throw new Error('Set DEMO_ADMIN_EMAIL and DEMO_ADMIN_PASSWORD (12+ characters)');
  }
  const db = new PrismaClient();
  try {
    await db.$transaction(async tx => {
      const existingUser = await tx.user.findFirst({ where: { email: adminEmail } });
      if (existingUser) throw new Error('Demo admin email already exists; choose a unique email');
      const tenant = await tx.tenant.create({ data: { name } });
      const admin = await tx.user.create({ data: {
        tenantId: tenant.id, email: adminEmail, passwordHash: await hash(adminPassword, 12),
        fullName: 'Demo Administrator', role: 'TENANT_ADMIN'
      }});
      await tx.kaizenProject.createMany({ data: [
        { tenantId: tenant.id, createdById: admin.id, title: 'Giảm thời gian chờ tại công đoạn đóng gói', description: 'Đo thời gian chờ, phân tích nguyên nhân và thử nghiệm PDCA.' },
        { tenantId: tenant.id, createdById: admin.id, title: 'Chuẩn hóa kiểm tra chất lượng đầu ca', description: 'Áp dụng checklist 5S và ghi nhận sai lỗi.' },
      ]});
      const definitions = [
        {code:'PRODUCTIVITY',name:'Năng suất dây chuyền',unit:'sp/h',target:100,warningMin:85,direction:'HIGHER_BETTER' as const},
        {code:'DEFECT_RATE',name:'Tỷ lệ lỗi',unit:'%',target:2,warningMax:4,direction:'LOWER_BETTER' as const},
      ];
      for (const def of definitions) await tx.kpiDefinition.create({data:{tenantId:tenant.id,...def}});
      const records = [];
      for (let i=0;i<21;i++) {
        const date = new Date(Date.UTC(2026,9,1+i,12));
        records.push({tenantId:tenant.id,metric:'PRODUCTIVITY',value:88+i*0.7+(i%3),unit:'sp/h',recordedAt:date});
        records.push({tenantId:tenant.id,metric:'DEFECT_RATE',value:4.4-i*0.09+(i%4)*0.05,unit:'%',recordedAt:date});
      }
      await tx.kpiRecord.createMany({data:records});
      console.log('Demo tenant created:',tenant.id,'KPI records:',records.length);
    },{timeout:20000});
  } finally { await db.$disconnect(); }
}
main().catch(err=>{console.error(err.message);process.exitCode=1;});
