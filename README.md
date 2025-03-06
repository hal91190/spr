# spr
Un script pour évaluer un ensemble de dépôts git.

Le projet est géré avec [uv](https://docs.astral.sh/uv/).

## Usage
```bash
spr
```

## Packaging

### Création de l'environnement virtuel
```bash
uv venv
```

### Activation de l'environnement virtuel
```bash
source .venv/bin/activate
```

### Build et installation
```bash
uv build
pipx install .
```
