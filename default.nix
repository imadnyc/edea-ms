with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
  name = "edea-ms";
  src = ./.;
  propagatedBuildInputs = [ pdm ];
	format = "pyproject";
	buildInputs = [ python3Packages.hatchling ];
}
