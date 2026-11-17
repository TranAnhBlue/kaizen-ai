import { IsNotEmpty, IsString, MaxLength } from 'class-validator';
export class CreateKaizenDto {
 @IsString() @IsNotEmpty() @MaxLength(180) title!: string;
 @IsString() @IsNotEmpty() @MaxLength(10000) description!: string;
}
