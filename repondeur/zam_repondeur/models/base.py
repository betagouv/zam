from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(
    sessionmaker(
        expire_on_commit=False,  # allow access to object attributes after commit
        extension=ZopeTransactionExtension(),  # attach to the transaction manager
    )
)
metadata = MetaData()
Base = declarative_base(metadata=metadata)
