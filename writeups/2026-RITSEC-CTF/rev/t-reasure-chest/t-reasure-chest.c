#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void function(unsigned char *, unsigned int, unsigned int *);
void change_var(unsigned int *, unsigned int *);

int main(void)
{
	unsigned char input[256];
	unsigned long long key[3];
	void *dest;
	unsigned int len;
	unsigned int len_mod8;
	unsigned int len_extend;
	unsigned char table[] = {0x38, 0x75, 0x5B, 0xCB, 0x44, 0xD2, 0xBE, 0x5D, 0x96, 0x9C, 0x56, 0x43, 0xEA, 0x98, 0x06, 0x75, 0x4A, 0x48, 0x13, 0xE6, 0xD4, 0xE8, 0x8E, 0x4F, 0x72, 0x70, 0x8B, 0xFF, 0xDC, 0x99, 0xF8, 0x76, 0xC5, 0xC9};
		
	memcpy(key, "tiny_encrypt_key", 16);

	printf("input : ");
	scanf("%s", input);

	len = strlen(input);
	len_mod8 = len % 8;

	len_extend = len + (len % 8);

	dest = malloc(len_extend);
	memcpy(dest, input, len);
	memset((unsigned char *)dest + len, 0, len_mod8);

	function((unsigned char *)dest, len_extend, (unsigned int *)key);

	printf("result : 0x");
	for (int i = 0; i < len_extend; i++)
		printf("%02X", ((unsigned char *)dest)[i]);

	putchar(10);

	if ((len_extend == 34) && !memcmp(dest, table, 0x22ULL))
		puts("Correct!");

	else
		puts("Wrong!");
	
	free(dest);

	return 0;
}

void function(unsigned char *dest, unsigned int len_extend, unsigned int *key)
{
	unsigned long long check_if = len_extend >> 2;
	unsigned long long var;

	for (int i = 0; i < (unsigned int)check_if; i++)
	{
		var = ((unsigned long long *)dest)[i];
		change_var((unsigned int *)&var, key);

		((unsigned long long *)dest)[i] = var;
	}

	return;
}

void change_var(unsigned int *var, unsigned int *key)
{
	unsigned int var1;
	unsigned int var0;
	unsigned int sum;

	var0 = var[0];
	var1 = var[1];
	sum = 0;

	for (int i = 0; i < 32; i++)
	{
		sum -= 1640531527;
		var0 += ((var1 >> 5) + key[1]) ^ (var1 + sum) ^ (16 * var1 + key[0]);
		var1 += ((var0 >> 5) + key[3]) ^ (var0 + sum) ^ (16 * var0 + key[2]);
	}

	var[0] = var0;
	var[1] = var1;

	return;
}
