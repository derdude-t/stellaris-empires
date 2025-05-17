{
  description = "Ein Python-Skript zum Entfernen leerer Zeilen aus einer Datei, mit automatischem Backup-Mechanismus.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      pkgsFor = system: import nixpkgs { inherit system; };

    in
    {
      packages = builtins.listToAttrs (map (system:
        let pkgs = pkgsFor system; in
        {
          name = system;
          value = {
            # Paket, das das Python-Skript direkt ausführt
            python-line-cleaner-raw = pkgs.writeShellApplication {
              name = "python-line-cleaner-raw"; # Name des ausführbaren Skripts
              runtimeInputs = [ pkgs.python3 ]; # Benötigt Python zur Laufzeit

              # Das Skript wird hier eingebettet. Nix kopiert tooling/empty_lines.py in den Store
              # und ersetzt ${./tooling/empty_lines.py} mit dem Pfad dorthin.
              text = ''
                #!${pkgs.stdenv.shell}
                exec ${pkgs.python3}/bin/python3 ${./tooling/empty_lines.py} "$@"
              '';

              meta = with pkgs.lib; {
                description = "Python-Skript zum Entfernen leerer Zeilen (direkter Ausführer).";
                homepage = null; # Oder Link zum Repo
                license = licenses.mit; # Annahme: MIT, anpassen falls nötig
                platforms = platforms.all; # Python ist plattformübergreifend
              };
            };

            # Wrapper-Skript, das Backup erstellt und dann das Python-Skript aufruft
            clean-empty-lines = pkgs.writeShellApplication {
              name = "clean-empty-lines"; # Name des ausführbaren Skripts
              runtimeInputs = [
                pkgs.coreutils  # Für 'cp' Befehl
                self.packages.${system}.python-line-cleaner-raw # Das Python-Skript-Paket
              ];

              text = ''
                #!${pkgs.stdenv.shell} # Verwendet die Standard-Shell der stdenv
                set -e # Bricht bei Fehlern sofort ab

                INPUT_FILE="$1"

                if [ -z "$INPUT_FILE" ]; then
                  echo "Benutzung: clean-empty-lines <EingabeDatei>" >&2
                  echo "Dieses Skript erstellt eine Sicherung von <EingabeDatei> als <EingabeDatei>.bak" >&2
                  echo "und bereinigt dann <EingabeDatei> direkt, indem leere Zeilen entfernt werden." >&2
                  exit 1
                fi

                if [ ! -f "$INPUT_FILE" ]; then
                    echo "Fehler: Eingabedatei '$INPUT_FILE' nicht gefunden." >&2
                    exit 1
                fi

                # Definiere den Namen der Backup-Datei.
                BACKUP_FILE="''${INPUT_FILE}.bak"

                echo "Erstelle Backup von '$INPUT_FILE' nach '$BACKUP_FILE'..."
                cp -f "$INPUT_FILE" "$BACKUP_FILE"

                echo "Bereinige '$INPUT_FILE' direkt mit Python-Skript..."
                # Das Python-Skript 'python-line-cleaner-raw' ist durch runtimeInputs im PATH verfügbar
                # Es wird aufgerufen, um die Datei direkt zu ändern (Input = Output)
                python-line-cleaner-raw "$INPUT_FILE" "$INPUT_FILE"

                echo "Datei '$INPUT_FILE' wurde bereinigt. Backup unter '$BACKUP_FILE' erstellt."
              '';
               meta = with pkgs.lib; { # Meta für das Wrapper-Skript
                description = "Wrapper-Skript zum Entfernen leerer Zeilen mit Backup (verwendet Python).";
                homepage = null;
                license = licenses.mit; # Anpassen falls nötig
                platforms = platforms.unix; # Shell-Skript
              };
            };
          };
        }) supportedSystems);

      defaultPackage = builtins.listToAttrs (map (system:
        {
          name = system;
          value = self.packages.${system}.clean-empty-lines; # Das Wrapper-Skript
        }) supportedSystems);

      apps = builtins.listToAttrs (map (system:
        {
          name = system;
          value = {
            clean-file = {
              type = "app";
              program = "${self.packages.${system}.clean-empty-lines}/bin/clean-empty-lines";
            };
            raw-clean = {
              type = "app";
              program = "${self.packages.${system}.python-line-cleaner-raw}/bin/python-line-cleaner-raw";
            };
          };
        }) supportedSystems);

      devShells = builtins.listToAttrs (map (system:
        let pkgs = pkgsFor system; in
        {
          name = system;
          value = {
            default = pkgs.mkShell {
              packages = [
                pkgs.python3 # Python-Interpreter
                # Füge hier weitere Python-Tools wie pip, flake8, black etc. hinzu, falls benötigt:
                # pkgs.python3Packages.pip
                # pkgs.python3Packages.flake8

                # Für einfaches Testen in der Dev-Shell:
                self.packages.${system}.clean-empty-lines # Das Wrapper Skript
                self.packages.${system}.python-line-cleaner-raw # Das reine Python Skript
              ];
            };
          };
        }) supportedSystems);
    };
}