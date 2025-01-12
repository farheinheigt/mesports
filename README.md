# MesPortsOuverts

MesPortsOuverts est un outil conçu pour analyser les ports ouverts sur un système macOS. Ce script utilise la commande `lsof` pour extraire les informations sur les connexions réseau, les services associés, et les processus en cours. Il affiche ces informations dans un tableau stylisé grâce à la bibliothèque `rich`. Bien que ce script soit actuellement adapté pour macOS, il pourrait facilement être adapté pour Linux dans de futures versions.

## Fonctionnalités principales

- Analyse des ports ouverts en utilisant `lsof`.
- Identification des services associés aux ports à l'aide de la base officielle de l'IANA.
- Affichage des connexions réseau avec des informations détaillées sur les processus.
- Présentation claire des résultats dans un tableau stylisé.

## Prérequis

- Python 3.x installé.
- Modules Python suivants :
  - `rich`
  - `requests`

## Installation

1. Clonez ce dépôt ou téléchargez le script.
2. Installez les dépendances Python requises avec pip :
   ```bash
   pip install rich requests
   ```

## Utilisation

### Alias recommandé
Pour une utilisation plus pratique, il est recommandé de créer un alias dans votre fichier shell (par exemple, `.zshrc` ou `.bashrc`) :

```bash
alias portsouverts='python3 /chemin/vers/mesportsouverts.py'
```

Rechargez ensuite votre terminal :

```bash
source ~/.zshrc  # ou ~/.bashrc
```

### Lancer le script

Pour exécuter le script, utilisez simplement :

```bash
portsouverts
```

Le script affichera les connexions réseau ouvertes sous forme de tableau détaillé.

## Contribution

Les contributions sont les bienvenues, en particulier pour l'adaptation de ce script à d'autres systèmes d'exploitation comme Linux.

1. Forkez le projet.
2. Créez une branche pour vos modifications :
   ```bash
   git checkout -b ma-nouvelle-fonctionnalite
   ```
3. Committez vos changements :
   ```bash
   git commit -m "Ajout d'une nouvelle fonctionnalité"
   ```
4. Poussez vos modifications :
   ```bash
   git push origin ma-nouvelle-fonctionnalite
   ```
5. Ouvrez une Pull Request.

## Licence

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus d'informations.

