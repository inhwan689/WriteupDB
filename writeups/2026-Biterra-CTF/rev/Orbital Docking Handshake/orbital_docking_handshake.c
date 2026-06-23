#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

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

int main(void)
{
	int offset = 0;
	char phrase[64];
	char window[32];
	char phrase2[13];
	
	puts("Orbital Docking Handshake");
	puts("Trace the handshake routine, recover the correct phrase, and align the approach window.");
	puts("Hint for analysis: the shortest path is still the cleanest one.");
	
	printf("Docking phrase: ");
	fflush(stdout);

	if (fgets(phrase, 64, stdin))
	{
		phrase[strcspn(phrase, "\n")] = 0;

		printf("Alignment window : ");
		fflush(stdout);

		if (fgets(window, 32, stdin))
		{
    		for (int i = 0; i < 0xC; i++)			// build_expected_phrase() 구현
    		{
        		unsigned char mask = 17 * i + 27;

        		phrase2[i] = obfuscated_phrase[i] ^ mask;
    		}

			phrase2[12] = 0;

			for (int i = 0; phrase2[i]; i++)		// compute_grid_offset() 구현
				offset += phrase2[i] * (i + 3);

			offset = offset % 1000 + 200;

			if (!strcmp(phrase, phrase2))
			{
				if (atoi(window) == offset)
				{
					puts("Docking accepted. Flag: ");
    				
					for (int i = 0; i < 0x21; i++)
        				printf("%c", encoded_flag[i] ^ (5 * i + phrase2[i % 0xC] + offset));
					
					return 0;
				}

				else
				{
					puts("Alignment window rejected.");

					return 1;
				}
			}

			else
			{
				puts("Handshake rejected. Docking denied.");

				return 1;
			}
		}

		else
		{
			puts("No alignment window supplied.");

			return 1;
		}
	}

	else
	{
		puts("No phrase supplied.");

		return 1;
	}

	return 0;
}
