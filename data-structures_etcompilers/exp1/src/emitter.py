class Emitter:
    def __init__(self):
        self.text = []
        self.data = []
        self.bss = []
        self.label_id = 0
        self.main = []

        # Solo lectura: SOLO literales
        self.data.append("section .rodata")
        self.data.append("bool_true:  db 'true', 0x0a, 0")
        self.data.append("bool_false: db 'false', 0x0a, 0")

        # Escritura: buffers/variables
        # Mover intbuf a .bss (writable), NO en .rodata
        self.bss.append("intbuf:     resb 32")

        # Código
        self.text.append("section .text")
        self.text.append("global _start")
        self.text += [
            "_start:",
            "    jmp __program_start",
            "",

            "print_bool:",
            "    ; rax contiene el bool (0/!=0)",
            "    cmp rax, 0",
            "    jne .t",
            "    mov rsi, bool_false",
            "    jmp .go",
            ".t:",
            "    mov rsi, bool_true",
            ".go:",
            "    ; calcular longitud hasta 0",
            "    mov rcx, rsi",
            "    xor rdx, rdx",
            ".blen:",
            "    cmp byte [rcx], 0",
            "    je .bdone",
            "    inc rcx",
            "    inc rdx",
            "    jmp .blen",
            ".bdone:",
            "    mov rax, 1      ; write",
            "    mov rdi, 1      ; fd=1",
            "    ; rsi ya apunta al inicio, rdx = len",
            "    syscall",
            "    ret",
            "",

            "print_int:",
            "    ; Entrada: rax = entero (signed)",
            "    ; Usamos: rbx, rcx, rdx, rsi, rdi (guardamos lo que pisamos)",
            "    push rbx",
            "    push rcx",
            "    push rdx",
            "    push rsi",
            "    push rdi",

            "    mov rbx, rax            ; trabajo",
            "    mov rcx, intbuf + 31    ; ptr de escritura (desde el final del buffer)",
            "    xor rsi, rsi            ; flag negativo (0=no,1=sí)",

            "    cmp rbx, 0",
            "    jge .ipos",
            "    neg rbx",
            "    mov rsi, 1",
            ".ipos:",
            "    mov byte [rcx], 0x0a    ; newline",
            "    dec rcx",

            "    cmp rbx, 0",
            "    jne .iconv",
            "    mov byte [rcx], '0'",
            "    dec rcx",
            "    jmp .iprefix",

            ".iconv:",
            ".iloop:",
            "    xor rdx, rdx            ; RDX:RAX / RDI",
            "    mov rax, rbx",
            "    mov rdi, 10",
            "    div rdi                  ; cociente->RAX, resto->RDX (0..9)",
            "    mov rbx, rax",
            "    add rdx, '0'",
            "    mov byte [rcx], dl",
            "    dec rcx",
            "    cmp rbx, 0",
            "    jne .iloop",

            ".iprefix:",
            "    cmp rsi, 0",
            "    je .iout",
            "    mov byte [rcx], '-'",
            "    dec rcx",

            ".iout:",
            "    inc rcx                 ; RCX apunta al primer byte del string",
            "    mov rsi, rcx            ; RSI = buffer",
            "    mov rdx, intbuf + 32",
            "    sub rdx, rcx            ; RDX = len = (intbuf+32) - RCX",
            "    mov rax, 1              ; write",
            "    mov rdi, 1              ; fd=1",
            "    syscall",

            "    pop rdi",
            "    pop rsi",
            "    pop rdx",
            "    pop rcx",
            "    pop rbx",
            "    ret",
        ]

    def fresh(self, prefix="L"):
        self.label_id += 1
        return f"{prefix}{self.label_id}"

    def emit(self, s): self.main.append(s)
    def emit_text(self, s): self.text.append(s)
    def emit_bss(self, s): self.bss.append(s)
    def emit_data(self, s): self.data.append(s)

    def finalize(self):
        self.text.append("__program_start:")
        self.text += self.main
        self.text += [
            "    mov rax, 60",    # exit
            "    xor rdi, rdi",
            "    syscall",
        ]
        out = []
        out += self.data
        out.append("section .bss")
        out += (self.bss if self.bss else ["    ; no globals"])
        out += self.text
        return "\n".join(out)
