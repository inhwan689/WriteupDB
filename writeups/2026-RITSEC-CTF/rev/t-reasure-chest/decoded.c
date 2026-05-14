#include <stdio.h>
#include <string.h>

void function(unsigned char *, unsigned int *);
void change_var(unsigned int *, unsigned int *);

int main(void)
{
	unsigned long long key[3];
	unsigned char table[] = {0x38, 0x75, 0x5B, 0xCB, 0x44, 0xD2, 0xBE, 0x5D, 0x96, 0x9C, 0x56, 0x43, 0xEA, 0x98, 0x06, 0x75, 0x4A, 0x48, 0x13, 0xE6, 0xD4, 0xE8, 0x8E, 0x4F, 0x72, 0x70, 0x8B, 0xFF, 0xDC, 0x99, 0xF8, 0x76, 0xC5, 0xC9};

	memcpy(key, "tiny_encrypt_key", 16);

	function(table, (unsigned int *)key);

	printf("%s\n", table);

	return 0;
}

void function(unsigned char *table, unsigned int *key)
{
	unsigned long long var;

	for (int i = 0; i < 8; i++)		// (len_extend)인 34 >> 2 == 8이므로
	{
		var = ((unsigned long long *)table)[i];
		change_var((unsigned int *)&var, key);

		((unsigned long long *)table)[i] = var;
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
	sum = -1640531527U * 32U;

	for (int i = 0; i < 32; i++)
	{
		var1 -= ((var0 >> 5) + key[3]) ^ (var0 + sum) ^ (16 * var0 + key[2]);
		var0 -= ((var1 >> 5) + key[1]) ^ (var1 + sum) ^ (16 * var1 + key[0]);
		sum += 1640531527U;
	}

	var[0] = var0;
	var[1] = var1;

	return;
}
