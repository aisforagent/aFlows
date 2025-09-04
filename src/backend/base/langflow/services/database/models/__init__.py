from .api_key import ApiKey
from .file import File
from .flow import Flow
from .folder import Folder
from .message import MessageTable
from .transactions import TransactionTable
from .user import User
from .variable import Variable

# Import SQLModel to get the metadata
from sqlmodel import SQLModel

# Create a custom metadata that excludes achat tables
from sqlalchemy import MetaData

# Get the original metadata
original_metadata = SQLModel.metadata

# Create a new metadata with only the tables we want
custom_metadata = MetaData()
achat_tables = {"achat_projects", "achat_threads", "achat_messages", "achat_artifacts", "achat_memory"}

# Copy only non-achat tables to the custom metadata
for table_name, table in original_metadata.tables.items():
    if table_name not in achat_tables:
        table.tometadata(custom_metadata)

# Replace the SQLModel metadata with our custom one
SQLModel.metadata = custom_metadata

__all__ = [
    "ApiKey",
    "File",
    "Flow",
    "Folder",
    "MessageTable",
    "TransactionTable",
    "User",
    "Variable",
]
