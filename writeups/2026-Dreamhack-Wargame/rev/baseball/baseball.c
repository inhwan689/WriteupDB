#include <stdio.h>
#include <stdlib.h>
#include <string.h>

unsigned char byte_4040[0x48];

unsigned char* base64(unsigned char*, unsigned long long, unsigned char*);

int main(int argc, char** argv)
{
	FILE* table_fp;
	unsigned long long table_file_size;
	FILE* input_fp;
	unsigned long long input_file_size;
	unsigned char* input_file;
	unsigned char* ptr;
	
	if (argc != 3)
	{
		printf("Usage : ./baseball <table filename> <input filename>\n");
		return 1;
	}

	table_fp = fopen(argv[1], "rb");
	if (!table_fp)
	{
		printf("File not found\n");
		return 1;
	}

	fseek(table_fp, 0LL, SEEK_END);
	table_file_size = ftell(table_fp);
	fseek(table_fp, 0LL, SEEK_SET);

	if (table_file_size != 64)
	{
		printf("Invalid table\n");
		fclose(table_fp);
		return 1;
	}

	fread(byte_4040, 0x41ULL, 1ULL, table_fp);
	fclose(table_fp);

	input_fp = fopen(argv[2], "rb");
	if (!input_fp)
	{
		printf("File not found\n");
		return 1;
	}
	
	fseek(input_fp, 0LL, SEEK_END);
	input_file_size = ftell(input_fp);

	if (!input_file_size)
	{
		printf("Invalid input\n");
		return 1;
	}
	
	fseek(input_fp, 0LL, SEEK_SET);
	
	input_file = malloc(input_file_size + 1);
	memset(input_file, 0, input_file_size + 1);
	fread(input_file, input_file_size, 1ULL, input_fp);
	fclose(input_fp);

	printf("%s\n", base64(input_file, input_file_size, ptr));

	free(input_file);
	free(ptr);

	return 0;
}

unsigned char* base64(unsigned char* input_file, unsigned long long input_file_size, unsigned char* ptr)
{
	unsigned long long size;
	unsigned char* input_file_start;
	unsigned char* input_file_end;
	unsigned char* byte_4040_ptr;

	size = (4 * input_file_size / 3 + 4) / 0x48ULL + 4 * input_file_size / 3 + 4 + 1;
	if (size < input_file_size)
		return NULL;

	ptr = malloc(size);

	input_file_end = &input_file[input_file_size];
	input_file_start = input_file;
	byte_4040_ptr = ptr;

	while (input_file_end - input_file_start > 2)
	{
		*(byte_4040_ptr + 0) = byte_4040[*(input_file_start + 0) >> 2];
		*(byte_4040_ptr + 1) = byte_4040[(*(input_file_start + 1) >> 4) | (*(input_file_start + 0) << 4) & 0x30];		// 0x30 == 0b 0011 0000
		*(byte_4040_ptr + 2) = byte_4040[(*(input_file_start + 2) >> 6) | (*(input_file_start + 1) << 2) & 0x3C];		// 0x3C == 0b 0011 1100
		*(byte_4040_ptr + 3) = byte_4040[*(input_file_start + 2) & 0x3F];												// 0x3F == 0b 0011 1111
		
		byte_4040_ptr += 4;
		input_file_start += 3;
	}

	if (input_file_end != input_file_start)
	{
		*byte_4040_ptr = byte_4040[*(input_file_start + 0) >> 2];

		if (input_file_end - input_file_start == 1)
		{
			*(byte_4040_ptr + 1) = byte_4040[(*input_file_start << 4) & 0x30];											// 0x30 == 0b 0011 0000
			*(byte_4040_ptr + 2) = '=';
		}

		else
		{
			*(byte_4040_ptr + 1) = byte_4040[(*(input_file_start + 1) >> 4) | (*(input_file_start + 0) << 4) & 0x30];	// 0x30 == 0b 0011 0000
			*(byte_4040_ptr + 2) = byte_4040[(*(input_file_start + 1) << 2) & 0x3C];									// 0x3C == 0b 0011 1100
		}

		*(byte_4040_ptr + 3) = '=';
		byte_4040_ptr += 4;
	}

	*byte_4040_ptr = 0;

	return ptr;
}
