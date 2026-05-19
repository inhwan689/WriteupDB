from pwn import ELF, context

context.log_level = 'error'

elf = ELF('./BasicIncome_Crackme', checksec=False)

dat_cmp = elf.read(0x47e0d0, 16)
dat_key = elf.read(0x47e0e0, 8)
dat_out = elf.read(0x47e0a0, 40)

input_bytes = bytes(dat_cmp[i] ^ dat_key[i % 8] for i in range(16))
voucher     = bytes(input_bytes[i % 16] ^ dat_out[i] for i in range(40))

print(voucher.decode('latin-1'))
