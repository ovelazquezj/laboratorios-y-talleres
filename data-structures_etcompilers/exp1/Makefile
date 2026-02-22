# --- MiniSEC Makefile (Docker-first) ---

PY=python3
PKG=src
BUILD=build

# Fuente por defecto (se puede sobreescribir con EX_SRC=examples/02_mod.ms)
EX_SRC?=examples/01_sum.ms

# ===== Ejecución nativa (host) =====
all: run

asm:
	$(PY) -m $(PKG).main $(EX_SRC) -o $(BUILD)/out.asm

assemble: asm
	nasm -felf64 $(BUILD)/out.asm -o $(BUILD)/out.o
	ld -o $(BUILD)/a.out $(BUILD)/out.o

run: assemble
	./build/a.out

#lexer:
#	???

# ===== Docker =====
IMAGE?=minigus

docker-build:
	docker build -t $(IMAGE) .

# Corre un ejemplo dentro del contenedor (parametrizable con EX_SRC=...)
docker-run:
	docker run --rm -it -v "$$(pwd)":/work $(IMAGE) make run EX_SRC=$(EX_SRC)

# Atajos para ejemplos frecuentes
docker-run-01:
	docker run --rm -it -v "$$(pwd)":/work $(IMAGE) make run EX_SRC=examples/01_sum.ms

docker-run-02:
	docker run --rm -it -v "$$(pwd)":/work $(IMAGE) make run EX_SRC=examples/02_mod.ms

# Corre una "suite mínima" (ambos ejemplos) dentro del contenedor
docker-test:
	docker run --rm -it -v "$$(pwd)":/work $(IMAGE) /bin/bash -lc "\
		set -e; \
		echo '>> Example 01'; make run EX_SRC=examples/01_sum.ms; echo; \
		echo '>> Example 02'; make run EX_SRC=examples/02_mod.ms; echo; \
		echo 'OK' \
	"
