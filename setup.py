#!/usr/bin/env python3
"""
Script de inicializacion para Telegram OSINT/CTI Platform.
Genera claves seguras y crea el archivo .env a partir de .env.example.
"""
import secrets
import os
import sys


def generate_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    example_path = os.path.join(os.path.dirname(__file__), ".env.example")

    if os.path.exists(env_path):
        print("[!] El archivo .env ya existe. Si desea regenerarlo, eliminel primero.")
        response = input("    Desea sobrescribirlo? (s/N): ").strip().lower()
        if response != "s":
            print("[!] Operacion cancelada.")
            return

    if not os.path.exists(example_path):
        print("[!] No se encontro .env.example")
        sys.exit(1)

    with open(example_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("[*] Generando claves seguras...")

    replacements = {
        "SECRET_KEY=": f"SECRET_KEY={secrets.token_hex(32)}",
        "INTERNAL_API_KEY=": f"INTERNAL_API_KEY={secrets.token_hex(32)}",
        "HASH_SALT=": f"HASH_SALT={secrets.token_hex(16)}",
        "REDIS_PASSWORD=": f"REDIS_PASSWORD={secrets.token_hex(16)}",
        "DB_PASSWORD=postgres": f"DB_PASSWORD={secrets.token_hex(16)}",
    }

    for old, new in replacements.items():
        content = content.replace(old, new, 1)

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("[+] Archivo .env generado exitosamente.")
    print("[!] IMPORTANTE: Edite el .env y complete los campos:")
    print("    - TG_API_ID y TG_API_HASH (obtener en https://my.telegram.org)")
    print("    - OPENAI_API_KEY (obtener en https://platform.openai.com)")
    print("    - SMTP_* (si desea reportes por email)")
    print("[+] Despues ejecute: docker-compose up --build -d")


if __name__ == "__main__":
    print("=" * 55)
    print("  Telegram OSINT/CTI Platform - Setup")
    print("=" * 55)
    generate_env()
