#include <stdio.h>
#include <stdint.h>
#include <string.h>

uint8_t obfuscated_phrase[] = {
    0x7F, 0x43, 0x5E, 0x25, 0x37, 0x11,
    0xEF, 0xF6, 0xD0, 0xCD, 0xAB, 0xB5,
};

uint8_t encoded_flag[] = {
    0xDA, 0xA1, 0xB5, 0xAD, 0xA4, 0xA8, 0x9B, 0xA0, 0xDF,
    0x88, 0x96, 0xDF, 0x80, 0x30, 0x91, 0x55, 0x68, 0x3A,
    0x7F, 0x7C, 0x1A, 0x58, 0x57, 0x75, 0x42, 0x70, 0x4C,
    0x32, 0x79, 0x28, 0x6B, 0x2E, 0x1A, 0x00, 0x00
};

unsigned char *itoa(int, unsigned char *);
unsigned int power(int, int);

int main(void)
{
	int offset = 0;
	unsigned char flag[0x21];
	unsigned char phrase[13];
	unsigned char window[32];
	unsigned char result[5];

	for (int i = 0; i < 0xC; i++)
	{
		unsigned char mask = 17 * i + 27;

		phrase[i] = obfuscated_phrase[i] ^ mask;
	}

	phrase[12] = 0;

	for (int i = 0; phrase[i]; i++)
		offset += phrase[i] * (i + 3);

	offset = offset % 1000 + 200;		// offset의 범위 : 200 ~ 1199

	itoa(offset, result);

	strcpy(window, result);

	for (int i = 0; i < 0x21; i++)
		flag[i] = encoded_flag[i] ^ (5 * i + phrase[i % 0xC] + offset);

	printf("%s", flag);

	return 0;
}

unsigned char *itoa(int offset, unsigned char *result)
{
	for (int i = 0; i < 5; i++)
	{
		int digit = offset / power(10, 4 - i);

		if (digit)
		{
			result[i] = digit;

			offset %= power(10, 4 - i);
		}		
	}

	result[4] = 0;

	return result;
}

unsigned int power(int a, int b)
{
	unsigned int result = 1;

	for (int i = 0; i < b; i++)
		result *= a;

	return result;
}
