{
  pkgs,
  pdm,
  python3Packages,
  buildNpmPackage,
  lib,
  fetchFromGitHub,
  makeWrapper,
  python3
}:

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
pkgs.python3Packages.buildPythonApplication rec {
  name = "edea_ms";
  src = ./.;
  format = "pyproject";
  dependencies = with pkgs.python3Packages; [
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
    uvicorn
  ];

  build-system = [ python3.pkgs.pdm-backend ];
  nativeBuildInputs = [ makeWrapper ];
  preBuild = ''
    cp -rv ${frontend}/static .
    ls ./static
    pwd
  '';
  
  meta = {
    description = "EDeA Measurement Server";
    homepage = "https://gitlab.com/edea-dev/edea-ms";
    license = lib.licenses.eupl12;
    maintainers = with lib.maintainers; [
      kiike
      rcoeurjoly
      amerino
    ];
    mainProgram = "edea_ms";
    platforms = lib.platforms.linux;
  };
    
} 
