#include <stdio.h>
#include <string.h>

int main(void)
{
	unsigned char input[] = "Pepero is a cookie stick, dipped in compound chocolate, manufactured by ????? Confectionery in South Korea\nPepero Day is held annually on November 11";
	unsigned char output[] = "7/OkZQIau/jou/R1by9acyjjutd0cUdlWshecQhkZUn1cUH1by9g4/9qNAn1byGaby9pbQSjWshgbUmqZAF+JtOBZUn1b8e1YoMPYoM1ny95ZAO+J/jaNAOB2vhrNLhVNDO0cshWNDIjbnrnZQhj4AM1S/Fmu/jou/GjN/n1bUm5JUFpNte1NyH1VA9yZUqLZQu13VR=";
	unsigned char table[65];
	unsigned char index[200];
	unsigned char alphabet[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

	memset(table, '?', 64);
	table[64] = '\0';

	int j = 0;

	for (int i = 0; j + 2 < 149; i += 4, j += 3)
	{
		index[i] = input[j] >> 2;
		index[i + 1] = (input[j + 1] >> 4) | ((input[j] << 4) & 0x30);
		index[i + 2] = (input[j + 2] >> 6) | ((input[j + 1] << 2) & 0x3C);
		index[i + 3] = input[j + 2] & 0x3F;
	}

	index[196] = input[147] >> 2;
	index[197] = (input[148] >> 4) | ((input[147] << 4) & 0x30);
	index[198] = (input[148] << 2) & 0x3C;

	for (int i = 0; i < 199; i++)
		table[index[i]] = output[i];

	printf("%s\n", table);

	printf("unused :");
	for (int a = 0; alphabet[a] != '\0'; a++)
	{
		unsigned char ch = alphabet[a];
		int unused = 1;

		for (int i = 0; i < 64; i++)
			if (ch == table[i])
			{
				unused = 0;
				break;
			}

		if (unused)
			printf(" %c", ch);
	}

	printf("\nunknown index :");
	for (int i = 0; i < 64; i++)
		if (table[i] == '?')
			printf(" %d", i);

	printf("\n");
	
	return 0;
}
