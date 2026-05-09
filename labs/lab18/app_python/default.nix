{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-24.11.tar.gz") {} }:

pkgs.python3Packages.buildPythonApplication {
  pname = "devops-info-service"; # Name of the package
  version = "1.0.0";             # Package version
  src = ./.;                     # Source directory (current directory)
  format = "other";              # Tells Nix we aren't using standard setup.py/pyproject.toml

  # Dependencies required for the application to run
  propagatedBuildInputs = with pkgs.python3Packages; [
    flask
    python-json-logger
    prometheus-client
  ];

  # Build-time tools (makeWrapper is needed to wrap the python script)
  nativeBuildInputs = [ pkgs.makeWrapper ];

  # Instructions to install the application and wrap it with its dependencies
  installPhase = ''
    mkdir -p $out/bin
    cp app.py $out/bin/devops-info-service
    chmod +x $out/bin/devops-info-service

    # Wraps the executable to ensure it uses the exact Nix-provided Python and PYTHONPATH
    wrapProgram $out/bin/devops-info-service \
      --prefix PYTHONPATH : "$PYTHONPATH"
  '';
}