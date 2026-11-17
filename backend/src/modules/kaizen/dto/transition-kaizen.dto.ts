import { IsIn, IsOptional, IsString, MaxLength } from 'class-validator';
export class TransitionKaizenDto {
 @IsIn(['SUBMIT','APPROVE','REJECT','START','COMPLETE','REOPEN']) action!: 'SUBMIT'|'APPROVE'|'REJECT'|'START'|'COMPLETE'|'REOPEN';
 @IsOptional() @IsString() @MaxLength(2000) comment?: string;
}
