Place your DrugCentral database dump (.sql or .sql.gz) here.

Files in this directory will be automatically executed by PostgreSQL
when the container starts for the first time.

Example:
  cp ~/Downloads/drugcentral.sql ./

The database will be initialized with this data when you run:
  docker compose up -d
