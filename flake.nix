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

        overlay = _: pkgs: {
          edea-ms = import ./default.nix {
            inherit pkgs;
            pdm = pkgs.pdm;
            python3Packages = pkgs.python3Packages;
            buildNpmPackage = pkgs.buildNpmPackage;
            lib = pkgs.lib;
            fetchFromGitHub = pkgs.fetchFromGitHub;
          };
        };

        finalPkgs = import nixpkgs {
          inherit system;
          overlays = [ overlay ];
        };
      in
      {
        devShell = finalPkgs.mkShell {
          buildInputs = [
            finalPkgs.poetry
            finalPkgs.nodejs
            finalPkgs.yarn
            finalPkgs.edea-ms
          ];

          shellHook = ''
            if [ ! -d "venv" ]; then
              python -m venv venv
              source venv/bin/activate
              pip install -U pip setuptools wheel
              poetry install
              yarn install
            else
              source venv/bin/activate
            fi
          '';
        };

        packages.default = finalPkgs.edea-ms;
      }
    );
}
