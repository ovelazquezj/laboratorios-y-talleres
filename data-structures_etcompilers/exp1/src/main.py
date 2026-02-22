# src/main.py
import argparse, subprocess
from pathlib import Path
from .parser import compile_source

def main():
    ap = argparse.ArgumentParser(description="MiniSEC (modular) → NASM ELF64")
    ap.add_argument("input", help="Fuente .ms")
    ap.add_argument("-o", "--output", default="build/out.asm", help="ASM de salida")
    ap.add_argument("--assemble", action="store_true", help="Invoca nasm+ld")
    ap.add_argument("--outfile", default="build/a.out", help="Binario de salida si se ensambla")
    args = ap.parse_args()

    src = Path(args.input).read_text(encoding="utf-8")
    asm = compile_source(src)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(asm, encoding="utf-8")
    print(f"[ok] Ensamblador generado: {args.output}")

    if args.assemble:
        obj = Path(args.output).with_suffix(".o")
        subprocess.check_call(["nasm","-felf64",args.output,"-o",str(obj)])
        Path(args.outfile).parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(["ld","-o",args.outfile,str(obj)])
        print(f"[ok] Ejecutable: {args.outfile}")

if __name__ == "__main__":
    main()
