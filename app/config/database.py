from functools import wraps
from typing import Annotated, Any, Optional, Tuple, Type, TypeVar

from fastapi import Depends
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy import create_engine, desc
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    OperationalError,
    ProgrammingError,
)
from sqlalchemy.orm import (
    Query,
    Session,
    declarative_base,
    registry,
    sessionmaker,
)
from sqlalchemy.sql.functions import coalesce
from starlette.requests import Request

from app.config.settings import Settings
from app.schemas.error import Error

Base = declarative_base()

engine = create_engine(Settings().DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

table_registry = registry()


def get_db(request: Request):
    db = request.state.db

    try:
        yield db
    finally:
        pass


DbSession = Annotated[Session, Depends(get_db)]

SqlAlchemyModel = TypeVar('SqlAlchemyModel')


def create(
    session: Session, model: SqlAlchemyModel
) -> Tuple[Optional[SqlAlchemyModel], Optional[Error]]:
    """
    Create a new model instance in the database.

    Args:
        session: SQLAlchemy session object.
        model: Model instance to be created.

    Returns:
        Tuple containing the created model instance and an error if any.
    """
    try:
        session.add(model)
        session.flush()

        return model, None
    except IntegrityError as e:
        return None, handle_db_error(session, model, e)  # type: ignore


def get_all(
    session: Session,
    model: Type[SqlAlchemyModel],
    page: int,
    page_size: int,
    filters: list,
) -> Tuple[list[SqlAlchemyModel], int]:
    """
    Get all instances of a model from the database.

    Args:
        session: SQLAlchemy session object.
        model: Model class to be queried.
        page: Page number.
        page_size: Number of instances per page.
        filters: List of filter conditions.

    Returns:
        Tuple containing the list of model instances and the total
        number of instances.
    """
    query: Query = session.query(model)

    if hasattr(model, 'updated_at'):
        query = query.order_by(
            desc(coalesce(model.updated_at, model.created_at))  # type: ignore
        )
    elif hasattr(model, 'created_at'):
        query = query.order_by(desc(model.created_at))  # type: ignore

    query = query.filter(*filters)

    total = query.count()
    query = query.offset((page - 1) * page_size)
    query = query.limit(page_size)

    return query.all(), total


def get_by_attribute(
    session: Session,
    model: Type[SqlAlchemyModel],
    attribute_name: str,
    attribute_value: Any,
    *,
    filters: list = [],
) -> Tuple[Optional[SqlAlchemyModel], Optional[Error]]:
    """
    Get a model instance by a specific attribute.

    Args:
        session: SQLAlchemy session object.
        model: Model class to be queried.
        attribute_name: Name of the attribute.
        attribute_value: Value of the attribute.

    Returns:
        Tuple containing the model instance and an error if any
    """
    entity = (
        session.query(model)  # type: ignore # CrudModel must be a SQLAlchemy model
        .filter(getattr(model, attribute_name) == attribute_value, *filters)
        .first()
    )
    if entity is None:
        return None, Error(
            error_code=404,
            error_message=(
                f'{model.__tablename__[:-1]} not found'
            ).capitalize(),  # type: ignore
        )

    return entity, None


def update(
    session: Session, model: Type[SqlAlchemyModel], id: int, **kwargs
) -> Optional[Error]:
    """
    Update a model instance in the database.

    Args:
        session: SQLAlchemy session object.
        model: Model class to be updated.
        id: ID of the model instance.
        **kwargs: Updated values.

    Returns:
        Error if any.
    """
    try:
        entity_update_status = (
            session.query(model)
            .filter(getattr(model, 'id') == id)
            .update(kwargs)  # type: ignore
        )

        if entity_update_status == 0:
            return Error(
                error_code=404,
                error_message=f'{model.__tablename__[:-1]} not found'  # type: ignore
                .capitalize(),
            )

        return None
    except IntegrityError as e:
        return None, handle_db_error(session, model, e)  # type: ignore


def delete(
    session: Session, model: Type[SqlAlchemyModel], id: int
) -> Optional[Error]:
    """
    Delete a model instance from the database.

    Args:
        session: SQLAlchemy session object.
        model: Model class to be deleted.
        id: ID of the model instance.

    Returns:
        Error if any.
    """
    entity, error = get_by_attribute(session, model, 'id', id)
    if error:
        return error

    session.delete(entity)

    return None


def commit(func):
    """
    Decorator to commit the session after a function is executed.

    Args:
        func: Function to be wrapped.

    Returns:
        Wrapped function.
    """

    @wraps(func)
    def wrapper(session: Session, *args, **kwargs):
        response, error = func(session, *args, **kwargs)

        if error:
            return None, error

        session.commit()

        return response, None

    return wrapper


def handle_db_error(
    session: Session, model: Type[SqlAlchemyModel], exception: Exception
) -> Error:
    """
    Handle common database errors such as integrity errors, operational errors,
    and unique constraint violations.

    Args:
        session: SQLAlchemy session object.
        model: The model class where the error occurred.
        exception: The exception raised during the operation.

    Returns:
        Error object with appropriate error message and code.
    """
    session.rollback()

    if isinstance(exception, ForeignKeyViolation):
        return Error(
            error_code=404, error_message='Related resource(s) not found'
        )

    if isinstance(exception, IntegrityError):
        unique_attrs = [
            column.name
            for column in model.__table__.columns  # type: ignore
            if column.unique
        ]
        violated_unique_attrs = []
        for attr in unique_attrs:
            if (
                session.query(model.__class__)  # type: ignore
                .filter(getattr(model.__class__, attr) == getattr(model, attr))
                .first()
                is not None
            ):
                violated_unique_attrs.append(attr)

        if violated_unique_attrs:
            return Error(
                error_code=409,
                error_message=(
                    f'{model.__tablename__[:-1]} already exists with '
                    f'these values: {", ".join(violated_unique_attrs)}'
                ).capitalize(),  # type: ignore
            )

    if isinstance(exception, OperationalError):
        return Error(
            error_code=500,
            error_message='Database connection error or timeout.',
        )

    if isinstance(exception, DataError):
        return Error(
            error_code=400,
            error_message='Invalid data type or value out of range.',
        )

    if isinstance(exception, ProgrammingError):
        return Error(
            error_code=400,
            error_message='SQL syntax error or invalid query structure.',
        )
    return Error(
        error_code=400, error_message='An unknown database error occurred.'
    )
