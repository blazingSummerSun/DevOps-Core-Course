{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-24.11.tar.gz") {} }:

let
  # Import our previously defined application derivation
  app = import ./default.nix { inherit pkgs; };
in
pkgs.dockerTools.buildLayeredImage {
  name = "devops-info-service-nix"; # Name of the output Docker image
  tag = "1.0.0";                    # Image tag
  contents = [ app ];               # What goes into the image (our app + its closure)

  config = {
    # The default command to run when container starts
    Cmd = [ "${app}/bin/devops-info-service" ];
    # Ports that should be exposed
    ExposedPorts = { "8000/tcp" = {}; };
  };

  # CRITICAL for reproducibility: sets the creation timestamp to Unix epoch (Jan 1, 1970)
  created = "1970-01-01T00:00:01Z";
}