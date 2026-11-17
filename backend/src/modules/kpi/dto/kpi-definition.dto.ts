import { IsEnum, IsNotEmpty, IsNumber, IsOptional, IsString, Matches, MaxLength } from 'class-validator';
export enum Direction { HIGHER_BETTER = 'HIGHER_BETTER', LOWER_BETTER = 'LOWER_BETTER' }
export class CreateKpiDefinitionDto {
 @IsString() @Matches(/^[A-Za-z0-9_-]{2,60}$/) code!: string;
 @IsString() @IsNotEmpty() @MaxLength(120) name!: string;
 @IsString() @IsNotEmpty() @MaxLength(30) unit!: string;
 @IsEnum(Direction) direction!: Direction;
 @IsOptional() @IsNumber() target?: number;
 @IsOptional() @IsNumber() warningMin?: number;
 @IsOptional() @IsNumber() warningMax?: number;
}
