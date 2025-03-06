#!/usr/bin/env python3

import subprocess


def run_checks():
    print("✅ Reformatage avec ruff")
    subprocess.run(["uvx", "ruff", "format"], check=True)
    print("✅ Vérification avec ruff")
    subprocess.run(["uvx", "ruff", "check"], check=True)
    print("✅ Vérification avec mypy")
    subprocess.run(["uvx", "mypy", "-p", "spr"], check=True)
    print("✨ 🌟 ✨ Vérifications terminées avec succès. ✨ 🌟 ✨")


if __name__ == "__main__":
    run_checks()
