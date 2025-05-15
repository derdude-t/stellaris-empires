# Stellaris Reiche

Notiz: Das README ist zu 90% GAI-generiert.
 
## user_empire_designs_v3.4.txt
 
Bitte am besten einfach über Stellaris selbst bearbeiten.
 
## Tooling: `user_empire_designs_v3.4.txt` automatisch bereinigen und sichern

ACHTUNG! Dieser Block ist nicht relevant, und sollte einfach nur regelmäßig alle paar Monate ausgeführt werden. Dieses Skript benötigt alles im `tooling` Ordner sowie `flake.nix` und `flake.lock`.

Dieses Projekt enthält ein Werkzeug (im Ordner `tooling` und konfiguriert durch `flake.nix`), um die Datei `user_empire_designs_v3.4.txt` (oder andere Textdateien) von überflüssigen Leerzeilen zu befreien. Dies kann helfen, die Datei sauber zu halten. Im Originalem hat die Datei mehrere Millionen leere Zeilen gehabt, die einfach durch das Spiel entstanden sind und schließlich selbst zur mehrfachen Löschung der Datei geführt

**Das Werkzeug erstellt automatisch eine Sicherungskopie (`<Dateiname>.bak`), bevor es die Originaldatei bereinigt und direkt überschreibt.**

### Verwendung des automatischen Bereinigungsskripts (mit Nix)

Voraussetzung: [NIX](https://nixos.org/download/) ist installiert (WSL2/Linux/MacOS) und befinden sich im aktuellem Hauptordner.

1. **Führen Sie das Bereinigungsskript für Ihre Datei aus:**
    Ersetzen Sie `user_empire_designs_v3.4.txt` durch den Pfad zu der Datei, die Sie bereinigen möchten.

    ```bash
    nix run . -- user_empire_designs_v3.4.txt
    ```

    * `nix run .`: Führt das in `flake.nix` als Standard definierte Werkzeug aus (welches das automatische Backup- und Bereinigungsskript ist).
    * `--`: Trennt die Nix-Optionen von den Argumenten, die an das Skript übergeben werden.
    * `user_empire_designs_v3.4.txt`: Die Zieldatei, die gesichert und anschließend bereinigt werden soll.

2. **Was dabei passiert:**
    * Das Skript erstellt **automatisch eine Sicherungskopie** der Originaldatei. Wenn Ihre Datei beispielsweise `meine_datei.txt` heißt, wird die Sicherung als `meine_datei.txt.bak` im selben Verzeichnis gespeichert.
    * Anschließend wird die Originaldatei (`user_empire_designs_v3.4.txt` im Beispiel oben) direkt geöffnet, von leeren Zeilen befreit und die Änderungen gespeichert (überschrieben).
    * Sie erhalten eine Bestätigungsmeldung über die ausgeführten Schritte im Terminal.

3. **Überprüfen (Empfohlen):**
    Es ist eine gute Praxis, die bereinigte Datei (`user_empire_designs_v3.4.txt`) kurz zu überprüfen. Die Sicherungskopie (`user_empire_designs_v3.4.txt.bak`) steht Ihnen zur Verfügung, falls etwas nicht wie erwartet funktioniert hat.

### Für fortgeschrittene Benutzer: Direkter Aufruf des Rust-Programms (ohne automatisches Backup)

Das zugrundeliegende Rust-Programm (`clean-empty-lines-bin`) kann auch direkt über die Nix-App `raw-clean` aufgerufen werden. Dies umgeht das automatische Backup- und Überschreib-Skript und gibt Ihnen volle Kontrolle über Ein- und Ausgabe, wie vom Rust-Programm ursprünglich vorgesehen:

* **Von Datei lesen und in eine andere Datei schreiben:**

    ```bash
    nix run .#raw-clean -- <EINGABEDATEI> <AUSGABEDATEI>
    ```

    Beispiel:

    ```bash
    nix run .#raw-clean -- user_empire_designs_v3.4.txt user_empire_designs_v3.4_manuell_bereinigt.txt
    ```

* **Von einer Datei lesen und die Ausgabe auf der Konsole (stdout) anzeigen:**

    ```bash
    nix run .#raw-clean -- <EINGABEDATEI>
    ```

    Beispiel:

    ```bash
    nix run .#raw-clean -- user_empire_designs_v3.4.txt
    ```

* **Von der Standardeingabe (stdin) lesen und auf der Konsole (stdout) ausgeben:**

    ```bash
    cat user_empire_designs_v3.4.txt | nix run .#raw-clean
    ```

    Oder um interaktiv Text einzugeben (Eingabe mit Strg+D beenden):

    ```bash
    nix run .#raw-clean
    ```