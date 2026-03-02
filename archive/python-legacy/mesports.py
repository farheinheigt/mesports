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
- subprocess : Pour exécuter la commande `lsof` et récupérer les résultats.
- socket : Pour obtenir le nom des services associés aux ports.
- rich : Pour afficher un tableau interactif et stylisé.
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
import os

from pathlib import Path
from rich.console import Console
from rich.table import Table

from get_iana_db import download_iana_csv


SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)
LOCAL_CSV_PATH = SCRIPT_DIR / "service-names-port-numbers.csv"


def load_iana_data():
    """
    Charge les données du fichier CSV de l'IANA.

    Returns:
        list[dict]: Une liste de dictionnaires contenant les données des ports et services.
    """
    with open(LOCAL_CSV_PATH, newline="", encoding="utf-8") as csvfile:
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
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        pass

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
    """
    cmd = ["lsof", "+c", "300", "-i", "-nP"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    lines = result.stdout.splitlines()[1:]
    connections = []

    for line in lines:
        parts = re.split(r"\s+", line)
        if len(parts) > 8:
            process_name = codecs.decode(parts[0], "unicode_escape")
            pid = parts[1]
            user = parts[2]
            protocol_network = parts[4] if len(parts) > 4 else ""
            protocol_session = parts[7]
            local_address_raw = parts[8]
            state = parts[9].strip("()").capitalize() if len(parts) > 9 else ""

            local_address, remote_address = "", ""
            if "->" in local_address_raw:
                local_address, remote_address = local_address_raw.split("->")
            else:
                local_address = local_address_raw

            local_match = re.search(r"(.*):(\d+)$", local_address)
            remote_match = re.search(r"(.*):(\d+)$", remote_address)

            local_ip, local_port = (
                (local_match.group(1), int(local_match.group(2)))
                if local_match
                else ("", 0)
            )
            remote_ip, remote_port = (
                (remote_match.group(1), int(remote_match.group(2)))
                if remote_match
                else ("", 0)
            )

            connections.append(
                {
                    "user": user,
                    "process_name": process_name,
                    "pid": pid,
                    "state": state,
                    "protocol_network": protocol_network,
                    "protocol_session": protocol_session,
                    "local_address": local_ip,
                    "local_port": local_port,
                    "service_name": "",
                    "remote_address": remote_ip if remote_ip else "*",
                    "remote_port": remote_port,
                }
            )

    return connections


def main():
    """
    Point d'entrée principal du script.
    """
    console = Console()

    _, e = download_iana_csv()
    if e:
        console.print(f"[orange][!][/orange] Erreur lors de la mise à jour de la base IANA : {e}")
        return

    console.print("[bold blue][+][/bold blue]Scanning open ports and processes...")

    connections = parse_lsof_output()
    console.print(f"{len(connections)} connexions trouvées :\n", style="bold green")

    connections.sort(key=lambda x: (x["process_name"], x["local_port"]))

    table = Table(
        style="magenta",
        header_style="bold white on magenta",
        row_styles=["", "dim"],
        box=None,
    )
    table.add_column("Utilisateur\n", style="white", justify="left")
    table.add_column("Type\n", style="cyan", justify="left")
    table.add_column("Protocole\n", style="cyan", justify="left")
    table.add_column("Adresse\nlocale", style="green", justify="right")
    table.add_column("Port\nlocal", style="yellow", justify="left")
    table.add_column("Service\n", style="magenta", justify="right")
    table.add_column("Processus\n", style="blue", justify="left")
    table.add_column("PID\n", style="red", justify="right")
    table.add_column("Adresse\ndistante", style="green", justify="right")
    table.add_column("Port\ndistant", style="yellow", justify="left")
    table.add_column("État\n", style="white", justify="left")

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

    console.print(table)


if __name__ == "__main__":
    main()
