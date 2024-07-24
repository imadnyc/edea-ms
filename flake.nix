{
  description = "Nix flake for edea-ms";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
          ];
        };

        packages.edea-ms = import ./default.nix {
          inherit pkgs;
          pdm = pkgs.pdm;
          python3Packages = pkgs.python3Packages;
          buildNpmPackage = pkgs.buildNpmPackage;
          lib = pkgs.lib;
          fetchFromGitHub = pkgs.fetchFromGitHub;
          python3 = pkgs.python3;
          makeWrapper = pkgs.makeWrapper;
        };
        
        packages.default = self.packages.edea-ms;
      }
    );
}
