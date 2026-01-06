"""
Configuración de Alembic para migraciones de base de datos.
"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Importar configuración y modelos
from app.core.config import settings
from app.db.base import Base

# Importar todos los modelos para que Alembic los detecte
from app.models import Universidad, Carrera, Estudiante, SesionConsultoria

# Configuración de Alembic
config = context.config

# Configurar URL de base de datos desde settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData para autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'.
    
    Genera SQL sin conectar a la base de datos.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecutar migraciones en modo 'online'.
    
    Conecta a la base de datos y ejecuta las migraciones.
    """
    from sqlalchemy import create_engine
    
    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detectar cambios en tipos de columnas
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
