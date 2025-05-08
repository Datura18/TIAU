{ pkgs }:
let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [ python-telegram-bot schedule ]);
in
{
  devShell = pkgs.mkShell {
    buildInputs = [ pythonEnv ];
  };
}
