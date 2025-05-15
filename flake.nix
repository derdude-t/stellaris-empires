{
  description = "Ein Rust-Skript zum Entfernen leerer Zeilen aus einer Datei, mit automatischem Backup-Mechanismus.";

  inputs = {
    # Wir verwenden nixpkgs als Quelle für die Rust-Toolchain und andere Pakete
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable"; # Kann auch einen stabilen Kanal verwenden
    # Oder einen spezifischen Commit für mehr Stabilität:
    # nixpkgs.url = "github:NixOS/nixpkgs/abcdef123456...";
  };

  outputs = { self, nixpkgs }:
    let
      # Liste der unterstützten Systeme (Architekturen)
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      # Eine Funktion, die die nixpkgs für ein bestimmtes System importiert
      pkgsFor = system: import nixpkgs { inherit system; };

    in
    {
      # Definiert Pakete für jedes unterstützte System
      packages = builtins.listToAttrs (map (system:
        let pkgs = pkgsFor system; in
        {
          name = system; # Name des Attributs im packages-Set (z.B. "x86_64-linux")
          value = {
            # Das ursprüngliche Rust-Binärpaket (umbenannt mit -bin Suffix)
            clean-empty-lines-bin = pkgs.rustPlatform.buildRustPackage {
              pname = "clean-empty-lines-bin"; # Eindeutiger Paketname für die Binärdatei
              version = "0.1.0";
              # Quelle ist der Unterordner 'tooling'
              src = ./tooling;
              # Cargo.lock Datei, die die genauen Abhängigkeiten sperrt
              cargoLock.lockFile = ./tooling/Cargo.lock;
              # Optionale Metadaten
              meta = with pkgs.lib; {
                description = "Rust-Binärprogramm zum Entfernen leerer Zeilen aus einer Datei.";
                homepage = null; # Oder Link zum Repo
                license = licenses.mit; # Oder die Lizenz deines Codes
                platforms = platforms.unix;
              };
            };

            # Wrapper-Skript, das Backup erstellt und dann das Rust-Binärprogramm aufruft
            clean-empty-lines = pkgs.writeShellApplication {
              name = "clean-empty-lines"; # Name des ausführbaren Skripts
              runtimeInputs = [ 
                pkgs.coreutils  # Für 'cp' Befehl
                self.packages.${system}.clean-empty-lines-bin # Das Rust-Binärprogramm
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

                # Definiere den Namen der Backup-Datei. Die \'\' sorgen für korrekte Nix String Interpolation.
                BACKUP_FILE="''${INPUT_FILE}.bak"

                echo "Erstelle Backup von '$INPUT_FILE' nach '$BACKUP_FILE'..."
                # cp ist durch pkgs.coreutils in runtimeInputs im PATH verfügbar
                cp -f "$INPUT_FILE" "$BACKUP_FILE"

                echo "Bereinige '$INPUT_FILE' direkt..."
                # Das Rust-Programm 'clean-empty-lines-bin' (pname) ist durch runtimeInputs im PATH verfügbar
                clean-empty-lines-bin "$INPUT_FILE" "$INPUT_FILE"

                echo "Datei '$INPUT_FILE' wurde bereinigt. Backup unter '$BACKUP_FILE' erstellt."
              '';
            };
          };
        }) supportedSystems);

      # Setzt das Standardpaket für `nix build` und `nix run . -- <Argumente>`
      # Dies zeigt nun auf unser Wrapper-Skript
      defaultPackage = builtins.listToAttrs (map (system:
        {
          name = system;
          value = self.packages.${system}.clean-empty-lines; # Das Wrapper-Skript
        }) supportedSystems);

      # Definiert 'apps' für `nix run .#<appname>`
      apps = builtins.listToAttrs (map (system:
        {
          name = system;
          value = {
            # App, um das Wrapper-Skript (Backup + Bereinigung) auszuführen
            # Kann mit `nix run .#clean-file -- <Dateiname>` oder `nix run .#<system>.clean-file -- <Dateiname>` ausgeführt werden
            clean-file = {
              type = "app";
              program = "${self.packages.${system}.clean-empty-lines}/bin/clean-empty-lines";
            };

            # App, um nur das Rust-Binärprogramm direkt auszuführen (ohne Backup)
            # Kann mit `nix run .#raw-clean -- <Eingabe> <Ausgabe>` oder `nix run .#<system>.raw-clean -- <Eingabe> <Ausgabe>` ausgeführt werden
            raw-clean = {
              type = "app";
              program = "${self.packages.${system}.clean-empty-lines-bin}/bin/clean-empty-lines-bin";
            };
          };
        }) supportedSystems);
      
      # Erstellt ein Attributset für die Entwicklungs-Shell über alle unterstützten Systeme
      devShells = builtins.listToAttrs (map (system:
        let pkgs = pkgsFor system; in
        {
          name = system; # Name des Attributs im devShells-Set
          value = {
            default = pkgs.mkShell {
              # Pakete, die in der Entwicklungs-Shell verfügbar sein sollen
              packages = [
                pkgs.rustc # Der Rust Compiler
                pkgs.cargo # Das Rust Build-Tool und Paketmanager
                # Füge hier weitere Tools wie rustfmt, clippy etc. hinzu, falls benötigt

                # Für einfaches Testen in der Dev-Shell:
                self.packages.${system}.clean-empty-lines # Das Wrapper Skript
                self.packages.${system}.clean-empty-lines-bin # Das reine Rust Binary
              ];
              # Optionale Umgebungsvariablen für die Shell
              # RUST_BACKTRACE = 1;
            };
          };
        }) supportedSystems);
    };
}