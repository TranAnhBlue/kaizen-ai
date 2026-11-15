import { IsNotEmpty, IsString, IsUUID, MaxLength } from 'class-validator';
export class CreateKaizenDto {
 @IsUUID() tenantId!: string; // DEMO ONLY: real tenant comes from authenticated principal
 @IsString() @IsNotEmpty() @MaxLength(180) title!: string;
 @IsString() @IsNotEmpty() description!: string;
}
