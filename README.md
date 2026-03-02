# MesPortsOuverts

MesPortsOuverts est maintenant un outil `zsh` base sur des utilitaires externes:
- collecte: `lsof`
- parsing: `jc`
- normalisation et tri: `jq`
- affichage interactif: `mestableaux`
- audit securite IA (optionnel): `ollama`

`messervices` est maintenant maintenu dans un projet distinct:
`~/Projets/network/messervices`.

Les anciens scripts Python sont conserves dans `archive/python-legacy/`.
La base IANA suivie dans le repo sert de copie de reference; le runtime utilise
par defaut un cache local non suivi sous `var/iana/`.

## Prerequis

- macOS (ou Linux avec `lsof` compatible)
- `zsh`
- `lsof`
- `jc`
- `jq`
- `mestableaux` pour le mode interactif
- alias de compatibilite encore accepte: `mestables`
- `curl` pour l'option Ollama

Installation rapide (macOS/Homebrew):

```bash
brew install jc jq
```

## Utilisation

Rendre le script executable (si besoin):

```bash
chmod +x ./bin/mesports
```

Lancer en mode interactif tabulaire (par defaut, `mestableaux`):

```bash
./bin/mesports
```

Mode texte simple:

```bash
./bin/mesports --ui plain
```

Afficher uniquement les sockets en ecoute:

```bash
./bin/mesports --listen-only
```

Lancer un audit securitaire via Ollama:

```bash
./bin/mesports --security-ollama --ollama-model qwen3:8b
```

Notes mode securite:
- `--security-ollama` n'ouvre pas l'interface tabulaire.
- Le script envoie directement un resume des connexions a Ollama.
- Si le terminal est interactif, un spinner Rust local est affiche pendant l'analyse.

Specifier une autre URL Ollama:

```bash
./bin/mesports --security-ollama --ollama-host http://localhost:11434
```

## Options CLI

```text
--ui <mestableaux|mestables|tabiew|plain>
--listen-only
--security-ollama
--ollama-model <model>
--ollama-host <url>
--no-iana-update
--action <info|kill|kill9>
--pid <pid[,pid...]>
--id <id[,id...]>
-h, --help
```

## Alias recommande

```bash
alias mesports='/chemin/vers/mesports/bin/mesports'
```

Puis:

```bash
source ~/.zshrc
```

Pour la documentation `messervices`, voir:
`~/Projets/network/messervices/README.md`.
