#!/usr/bin/env python3

"""
Module de scan des ports ouverts et identification des services.

Ce module utilise la commande `lsof` pour détecter les ports en écoute sur 
le système local et tente d'identifier les services associés à ces ports en 
utilisant la bibliothèque `socket` et la base officielle de l'IANA. Les résultats 
sont affichés dans un tableau stylisé grâce à la bibliothèque `rich`.

Fonctionnalités principales :
- Analyse les ports ouverts via `lsof`.
- Associe les numéros de ports aux services standards (TCP/UDP avec version).
- Utilise la base IANA pour des informations officielles.
- Affiche les informations dans un tableau coloré avec des détails sur le processus.

Modules utilisés :
- subprocess :  Pour exécuter la commande `lsof` et récupérer les résultats.
- socket :      Pour obtenir le nom des services associés aux ports.
- rich :        Pour afficher un tableau interactif et stylisé.
- get_iana_db : Pour charger ou télécharger la base IANA.

Comment utiliser :
1. Exécuter ce script directement dans un terminal Python :
   ```bash
   python mesportsouverts_updated.py
   ```
2. Observez les ports ouverts, les services associés et les processus correspondants.
"""

import subprocess
import socket
import re
import csv
import codecs

from pathlib      import Path
from rich.console import Console
from rich.table   import Table

from get_iana_db  import download_iana_csv

# Constantes
LOCAL_CSV_PATH = Path("service-names-port-numbers.csv")

def load_iana_data():
    """
    Charge les données du fichier CSV de l'IANA.

    Returns:
        list[dict]: Une liste de dictionnaires contenant les données des ports et services.
    """
    with open(LOCAL_CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def get_service_name(port):
    """
    Recherche un service associé à un port.

    Args:
        port (int): Le numéro de port à analyser.

    Returns:
        str: Le nom du service ou "Unknown Service" si non trouvé.
    """
    # Rechercher dans la base locale avec socket
    try:
        return socket.getservbyport(port, 'tcp')
    except OSError:
        pass  # Fallback vers la base IANA

    # Rechercher dans la base IANA
    iana_data = load_iana_data()
    for row in iana_data:
        if row["Port Number"] == str(port) and row["Transport Protocol"] == "tcp":
            return row["Service Name"] or "Unknown Service"
    return "Unknown Service"

def parse_lsof_output():
    """
    Exécute la commande `lsof -i -nP` et extrait les détails des connexions ouvertes.

    Returns:
        list[dict]: Une liste de dictionnaires contenant les informations des connexions.
        Chaque dictionnaire contient :
        - "protocol" : Type de connexion (TCP4, UDP6, etc.).
        - "address"  : Adresse locale sur laquelle le socket écoute.
        - "port"     : Port associé à l'adresse locale.
        - "state"    : État de la connexion (LISTEN, ESTABLISHED, etc.).
        - "process_name"  : Nom du processus.
        - "pid"      : Identifiant du processus (PID).
        - "user"     : Utilisateur du processus.
    """
    cmd         = ["lsof", "+c", "300", "-i", "-nP"]
    result      = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    lines       = result.stdout.splitlines()[1:]  # Ignorer l'en-tête
    connections = []

    for line in lines:
        parts = re.split(r"\s+", line)
        if len(parts) > 8:  # Vérifier que toutes les colonnes sont présentes
            process_name        = codecs.decode(parts[0], 'unicode_escape')
            pid                 = parts[1]
            user                = parts[2]
            protocol_network    = parts[4] if len(parts) > 4 else ""
            protocol_session    = parts[7]
            local_address_raw   = parts[8]
            state               = parts[9].strip("()").capitalize() if len(parts) > 9 else ""

            # Extraire l'adresse locale et distante
            local_address, remote_address = "", ""
            if "->" in local_address_raw:
                local_address, remote_address = local_address_raw.split("->")
            else:
                local_address = local_address_raw

            # Extraire le port et l'adresse depuis local_address
            local_match  = re.search(r"(.*):(\d+)$", local_address)
            remote_match = re.search(r"(.*):(\d+)$", remote_address)

            local_ip,  local_port  = (local_match.group(1),  int(local_match.group(2)))  if local_match  else ("", 0)
            remote_ip, remote_port = (remote_match.group(1), int(remote_match.group(2))) if remote_match else ("", 0)

            # Ajouter les informations dans la liste des connexions
            connections.append({
                "user":             user,
                "process_name":     process_name,
                "pid":              pid,
                "state":            state,
                "protocol_network": protocol_network,
                "protocol_session": protocol_session,
                "local_address":    local_ip,
                "local_port":       local_port,
                "service_name":     "",
                "remote_address":   remote_ip if remote_ip else "*",
                "remote_port":      remote_port,
            })

    return connections

def main():
    """
    Point d'entrée principal du script.

    Cette fonction :
    1. Vérifie et met à jour la base IANA si nécessaire.
    2. Scanne les ports en écoute sur le système.
    3. Associe chaque port en écoute à son service.
    4. Affiche les résultats dans un tableau stylisé avec `rich`.
    """
    console = Console()

    # Vérifier et télécharger la base IANA
    _, e = download_iana_csv()
    if e:
        console.print(f"[orange][!][/orange] Erreur lors de la mise à jour de la base IANA : {e}")
        return

    console.print("[bold blue][+][/bold blue]Scanning open ports and processes...")

    # Récupérer les connexions avec leurs processus
    connections = parse_lsof_output()
    console.print(f"{len(connections)} connexions trouvées :\n", style="bold green")

    # Trier les connexions par processus, puis par numéro de port
    connections.sort(key=lambda x: (x["process_name"], x["local_port"]))

    # Créer un tableau pour afficher les résultats
    table = Table(
        style           = "magenta",
        header_style    = "bold white on magenta",  # Style général des en-têtes
        row_styles      = ["", "dim"],  # Alternance de luminosité des lignes
        box             = None  # Pas de bordures
    )
    table.add_column("Utilisateur\n",      style="white",   justify="left")
    table.add_column("Type\n",             style="cyan",    justify="left")
    table.add_column("Protocole\n",        style="cyan",    justify="left")
    table.add_column("Adresse\nlocale",    style="green",   justify="right")
    table.add_column("Port\nlocal",        style="yellow",  justify="left")
    table.add_column("Service\n",          style="magenta", justify="left")
    table.add_column("Processus\n",        style="blue",    justify="left")
    table.add_column("PID\n",              style="red",     justify="right")
    table.add_column("Adresse\ndistante",  style="green",   justify="right")
    table.add_column("Port\ndistant",      style="yellow",  justify="left")
    table.add_column("État\n",             style="white",   justify="left")

    for conn in connections:
        service_name = get_service_name(conn["local_port"])
        table.add_row(
            conn["user"],
            conn["protocol_network"],
            conn["protocol_session"],
            conn["local_address"].strip(),
            str(conn["local_port"]),
            service_name,
            conn["process_name"],
            conn["pid"],
            conn["remote_address"].strip(),
            str(conn["remote_port"]),
            conn["state"],
        )

    # Afficher le tableau
    console.print(table)

if __name__ == "__main__":
    main()
