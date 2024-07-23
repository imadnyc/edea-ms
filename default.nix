# {
#   pkgs,
#   pdm,
#   python3Packages,
#   buildNpmPackage,
#   lib,
#   fetchFromGitHub
# }:

with import /home/a/son/nixpkgs { };

let
  frontend = buildNpmPackage rec {
    pname = "edea-ms";
    version = "0.2.0";

    src = ./.;

    npmDepsHash = "sha256-eHjgyFEeLIpAfl5UG5AlhHRsH9Lt/oxPLOOMCLm6JZ0=";

    # The prepack script runs the build script, which we'd rather do in the build phase.
    # npmPackFlags = [ "--ignore-scripts" ];

    # NODE_OPTIONS = "--openssl-legacy-provider";
    installPhase = ''
      mkdir $out
      cp -rv ./static $out
    '';
  };
in
pkgs.python3Packages.buildPythonPackage {
  name = "edea-ms";
  src = ./.;
  format = "pyproject";
  propagatedBuildInputs = [
    pdm
    python3Packages.uvicorn
    #frontend
  ];
  nativeBuildInputs = with pkgs.python3Packages; [
    aiofiles
    python-multipart
    hatchling
    pyjwt
    fastapi
    sqlalchemy
    alembic
    authlib
    httpx
    polars
    cryptography
    itsdangerous
    pyarrow
    aiosqlite
  ];
  postBuild = ''
    cp -rv ${frontend}/static .
    ls ./static
    pwd
  '';
  postInstall = ''
    #cp -rv ${frontend}/static $out
  '';
}
