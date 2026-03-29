export DB_HOST="localhost"
export DB_PORT="5432"
envsubst '$DB_HOST,$DB_PORT' < config.template > config.conf
