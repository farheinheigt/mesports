#compdef mesports

_mesports() {
  _arguments -s \
    '--ui[Mode d affichage]:mode:(mestableaux mestables tabiew plain)' \
    '--listen-only[Afficher uniquement les sockets LISTEN]' \
    '--security-ollama[Lancer une analyse securitaire via Ollama]' \
    '--ollama-model[Nom du modele Ollama]:model' \
    '--ollama-host[URL du serveur Ollama]:url:_urls' \
    '--no-iana-update[Ne pas mettre a jour la base IANA]' \
    '--action[Action sur un PID]:action:(info kill kill9)' \
    '--pid[PID cible, ou liste separee par virgules]:pid' \
    '--id[ID cible depuis la liste]:id' \
    '(-h --help)'{-h,--help}'[Afficher l aide]'
}

_mesports "$@"
