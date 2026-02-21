{ pkgs ? import <nixpkgs> {} }:

let
  pythonPackages = ps: with ps; [
    flask
    flask-sqlalchemy
    python-dotenv
    google-api-python-client
    google-auth
    google-auth-oauthlib
    google-auth-httplib2
    flask-wtf
    flask-limiter
    flask-compress
    werkzeug
    gunicorn
    psycopg2
    email-validator
    apscheduler
    requests
  ];
  python = pkgs.python310.withPackages pythonPackages;
in
pkgs.mkShell {
  buildInputs = [
    python
    pkgs.postgresql
    pkgs.honcho
  ];

  shellHook = ''
    export FLASK_APP=app
    export FLASK_ENV=development
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/stn_diklat"
    export SECRET_KEY="a-super-secret-key-for-dev"
    
    echo "Nix environment is ready."
    echo "Starting the application automatically..."
    honcho start
  '';
}
