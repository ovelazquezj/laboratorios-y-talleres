section .rodata
bool_true:  db 'true', 0x0a, 0
bool_false: db 'false', 0x0a, 0
section .bss
intbuf:     resb 32
var_n: resq 1
var_i: resq 1
var_sum: resq 1
var_a: resq 5
section .text
global _start
_start:
    jmp __program_start

print_bool:
    ; rax contiene el bool (0/!=0)
    cmp rax, 0
    jne .t
    mov rsi, bool_false
    jmp .go
.t:
    mov rsi, bool_true
.go:
    ; calcular longitud hasta 0
    mov rcx, rsi
    xor rdx, rdx
.blen:
    cmp byte [rcx], 0
    je .bdone
    inc rcx
    inc rdx
    jmp .blen
.bdone:
    mov rax, 1      ; write
    mov rdi, 1      ; fd=1
    ; rsi ya apunta al inicio, rdx = len
    syscall
    ret

print_int:
    ; Entrada: rax = entero (signed)
    ; Usamos: rbx, rcx, rdx, rsi, rdi (guardamos lo que pisamos)
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    mov rbx, rax            ; trabajo
    mov rcx, intbuf + 31    ; ptr de escritura (desde el final del buffer)
    xor rsi, rsi            ; flag negativo (0=no,1=sí)
    cmp rbx, 0
    jge .ipos
    neg rbx
    mov rsi, 1
.ipos:
    mov byte [rcx], 0x0a    ; newline
    dec rcx
    cmp rbx, 0
    jne .iconv
    mov byte [rcx], '0'
    dec rcx
    jmp .iprefix
.iconv:
.iloop:
    xor rdx, rdx            ; RDX:RAX / RDI
    mov rax, rbx
    mov rdi, 10
    div rdi                  ; cociente->RAX, resto->RDX (0..9)
    mov rbx, rax
    add rdx, '0'
    mov byte [rcx], dl
    dec rcx
    cmp rbx, 0
    jne .iloop
.iprefix:
    cmp rsi, 0
    je .iout
    mov byte [rcx], '-'
    dec rcx
.iout:
    inc rcx                 ; RCX apunta al primer byte del string
    mov rsi, rcx            ; RSI = buffer
    mov rdx, intbuf + 32
    sub rdx, rcx            ; RDX = len = (intbuf+32) - RCX
    mov rax, 1              ; write
    mov rdi, 1              ; fd=1
    syscall
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret
__program_start:
    lea rdi, [var_n]
    mov rax, 5
    mov [rdi], rax
    lea rdi, [var_i]
    mov rax, 0
    mov [rdi], rax
    lea rdi, [var_sum]
    mov rax, 0
    mov [rdi], rax
Lwhile1:
    mov rax, [var_i]
    push rax
    mov rax, [var_n]
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setl  al
    movzx rax, al
    cmp rax, 0
    je Lendw2
    mov rax, [var_i]
    lea rdi, [var_a]
    mov rbx, rax
    imul rbx, 8
    add rdi, rbx
    mov rax, [var_i]
    push rax
    mov rax, 2
    mov rbx, rax
    pop rax
    imul rax, rbx
    mov [rdi], rax
    lea rdi, [var_sum]
    mov rax, [var_sum]
    push rax
    mov rax, [var_i]
    lea rbx, [var_a]
    imul rax, 8
    add rbx, rax
    mov rax, [rbx]
    mov rbx, rax
    pop rax
    add rax, rbx
    mov [rdi], rax
    lea rdi, [var_i]
    mov rax, [var_i]
    push rax
    mov rax, 1
    mov rbx, rax
    pop rax
    add rax, rbx
    mov [rdi], rax
    jmp Lwhile1
Lendw2:
    mov rax, [var_sum]
    push rax
    mov rax, 10
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setg  al
    movzx rax, al
    cmp rax, 0
    je Lelse3
    mov rax, 1
    call print_bool
    jmp Lendif4
Lelse3:
    xor rax, rax
    call print_bool
Lendif4:
    mov rax, [var_sum]
    call print_int
    mov rax, 60
    xor rdi, rdi
    syscall