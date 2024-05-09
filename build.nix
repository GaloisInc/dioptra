{
  lib,
  stdenv,
  buildPythonApplication,
  setuptools,
  wheel,
}:

buildPythonApplication rec {
  pname = "dioptra";
  version = "0.0.1";
  pyproject = true;

  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.unions [
      ./pyproject.toml
      ./README.md
      ./src
    ];
  };

  nativeBuildInputs = [ setuptools wheel ];
}
