{
  description = "Ein Rust-Skript zum Entfernen leerer Zeilen aus einer Datei.";

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

      # Erstellt ein Attributset für die Pakete über alle unterstützten Systeme
      packages = builtins.listToAttrs (map (system:
        let pkgs = pkgsFor system; in
        {
          name = system; # Name des Attributs im packages-Set
          value = {
            # Definiert das Paket für unser Rust-Skript
            clean-empty-lines = pkgs.rustPlatform.buildRustPackage {
              pname = "clean-empty-lines"; # Paketname
              version = "0.1.0";          # Paketversion
              # Quelle ist jetzt der Unterordner 'tooling'
              src = ./tooling;

              # Cargo.lock Datei, die die genauen Abhängigkeiten sperrt
              # Stelle sicher, dass diese Datei im 'tooling'-Ordner existiert!
              cargoLock.lockFile = ./tooling/Cargo.lock;

              # Optionale Metadaten
              meta = with pkgs.lib; {
                description = "Ein Rust-Skript zum Entfernen leerer Zeilen aus einer Datei."; # Explizit hier definieren
                homepage = null; # Oder Link zum Repo
                license = licenses.mit; # Oder die Lizenz deines Codes
                platforms = platforms.unix; # Oder spezifischer
              };
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
              ];
              # Optionale Umgebungsvariablen für die Shell
              # RUST_BACKTRACE = 1;
            };
          };
        }) supportedSystems);

    in
    {
      # Exportiere die definierten Pakete und devShells
      packages = packages;
      devShells = devShells;

      # Setze das Standardpaket für einfaches `nix build` und `nix run`
      defaultPackage = builtins.listToAttrs (map (system:
         let pkgs = pkgsFor system; in
         { name = system; value = packages.${system}.clean-empty-lines; }) supportedSystems);
    };
}
