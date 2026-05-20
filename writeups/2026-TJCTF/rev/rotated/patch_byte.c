#include <stdio.h>

int main(void)
{
	FILE* in;
	FILE* out;
	int c;

	in = fopen("chall", "rb");
	out = fopen("chall_patch", "wb");

	while ((c = fgetc(in)) != EOF)
	{
		unsigned char binary = (unsigned char)c;
		binary -= 0x1D;
		fputc(binary, out);
	}

	fclose(in);
	fclose(out);

	return 0;
}
