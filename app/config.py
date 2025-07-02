import os
from pathlib import Path
import configparser

_CFG_DIR = Path(__file__).resolve().parent.parent / "config"

def _read_properties(file_name):
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.read(_CFG_DIR / file_name)
    return {k: v for section in parser.sections() for k, v in parser[section].items()}

AWS_CFG = _read_properties("aws.properties")
PG_CFG = _read_properties("postgres.properties")

S3_BUCKET = AWS_CFG["bucket"]
PG_DSN = (
    f"host={PG_CFG['host']} port={PG_CFG['port']} dbname={PG_CFG['dbname']} "
    f"user={PG_CFG['user']} password={PG_CFG['password']} sslmode={PG_CFG['sslmode']}"
)
