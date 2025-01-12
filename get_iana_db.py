#!/usr/bin/env python3

"""
Module de gestion de la base IANA des noms de services et des numéros de ports.

Ce module est responsable uniquement du téléchargement et de la mise à jour 
de la base de données officielle de l'IANA au format CSV. 

Fonctionnalités :
- Téléchargement automatique du fichier CSV de l'IANA.
- Mise à jour conditionnelle selon une période d'un jour.

Modules requis :
- csv
- pathlib
- datetime
- requests
- rich

"""

from pathlib        import Path
from datetime       import datetime, timedelta
import requests
from rich.console   import Console
from rich.progress  import SpinnerColumn, Progress

# Constantes
IANA_CSV_URL   = "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv"
LOCAL_CSV_PATH = Path("service-names-port-numbers.csv")
console = Console()

def is_update_needed():
    """
    Vérifie si une mise à jour est nécessaire en se basant sur la date de 
    dernière modification du fichier local.

    Returns:
        bool: True si le fichier doit être mis à jour, sinon False.
    """
    if not LOCAL_CSV_PATH.exists():
        return True  # Aucun fichier local, besoin de télécharger

    # Obtenir la date de dernière modification du fichier
    last_modified = datetime.fromtimestamp(LOCAL_CSV_PATH.stat().st_mtime)

    # Comparer la date actuelle avec la dernière modification
    return datetime.now() > last_modified + timedelta(days=1)

def download_iana_csv():
    """
    Télécharge le fichier CSV de l'IANA si une mise à jour est nécessaire.

    Returns:
        bool: True si le téléchargement réussit, False en cas d'échec.
    """
    try:
        if is_update_needed():
            with Progress(SpinnerColumn(), "[bold magenta]Téléchargement de la base IANA des ports et services...", console=console) as progress:
                task = progress.add_task("download")
                response = requests.get(IANA_CSV_URL, timeout=10)
                response.raise_for_status()  # Vérifie les erreurs HTTP
                LOCAL_CSV_PATH.write_bytes(response.content)
                progress.update(task, completed=100)
            console.print("[bold green][+][/bold green] Base IANA téléchargée avec succès.")
        return True, None
    except Exception as e:
        return False, e

if __name__ == "__main__":
    download_iana_csv()
