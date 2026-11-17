import { IsDateString, IsNotEmpty, IsNumber, IsString, MaxLength } from 'class-validator';
export class CreateKpiDto {
 @IsString() @IsNotEmpty() @MaxLength(120) metric!: string;
 @IsNumber({ maxDecimalPlaces: 4 }) value!: number;
 @IsString() @IsNotEmpty() @MaxLength(30) unit!: string;
 @IsDateString() recordedAt!: string;
}
