with import <nixpkgs> {};

pkgs.python3Packages.buildPythonPackage {
  name = "edea-ms";
  src = ./.;
	format = "pyproject";
  propagatedBuildInputs = [ pdm python3Packages.uvicorn ];
  nativeBuildInputs = with pkgs.python3Packages; [
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
}
