import datetime
from peewee import (
    SqliteDatabase, Model, CharField, TextField, IntegerField,
    DateTimeField, ForeignKeyField,
)
import os

DB_PATH = os.environ.get("CAZZKB_DB_PATH", "data/cazzkb.db")

db = SqliteDatabase(DB_PATH, pragmas={
    "journal_mode": "wal",
    "foreign_keys": 1,
}, check_same_thread=False)


class BaseModel(Model):
    class Meta:
        database = db


class KnowledgeBase(BaseModel):
    name = CharField(unique=True)
    description = TextField(default="")
    config = TextField(default="{}")  # JSON string of kb-specific overrides
    chunk_count = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)


class Document(BaseModel):
    kb = ForeignKeyField(KnowledgeBase, backref="documents", on_delete="CASCADE")
    filename = CharField()
    title = CharField(default="")
    source_type = CharField(default="markdown")  # markdown|pdf|docx|web|audio|image
    summary = TextField(default="")
    enabled = IntegerField(default=1)            # SQLite-friendly bool
    source_date = CharField(default="")       # from frontmatter or filename
    categories = TextField(default="[]")       # JSON array
    tags = TextField(default="[]")             # JSON array
    chunk_count = IntegerField(default=0)
    ingested_at = DateTimeField(default=datetime.datetime.utcnow)


class Chunk(BaseModel):
    document = ForeignKeyField(Document, backref="chunks", on_delete="CASCADE")
    content = TextField()
    header_path = CharField(default="")        # e.g. "/SSM基础/连续时间模型"
    element_type = CharField(default="text")   # header|code|table|text|list|quote
    chunk_index = IntegerField()
    metadata_json = TextField(default="{}")    # extra metadata as JSON
    created_at = DateTimeField(default=datetime.datetime.utcnow)


class Conversation(BaseModel):
    kb = ForeignKeyField(KnowledgeBase, backref="conversations", on_delete="CASCADE")
    title = CharField(default="New Chat")
    created_at = DateTimeField(default=datetime.datetime.utcnow)


class Message(BaseModel):
    conversation = ForeignKeyField(Conversation, backref="messages", on_delete="CASCADE")
    role = CharField()                          # user | assistant
    content = TextField()
    sources_json = TextField(default="[]")      # cited chunk IDs
    created_at = DateTimeField(default=datetime.datetime.utcnow)


class Artifact(BaseModel):
    kb = ForeignKeyField(KnowledgeBase, backref="artifacts", on_delete="CASCADE")
    title = CharField()
    artifact_type = CharField(default="note")    # note|briefing|faq|study_guide|timeline|mind_map
    content = TextField()
    metadata_json = TextField(default="{}")
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)


def _column_exists(table: str, column: str) -> bool:
    rows = db.execute_sql(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def _ensure_column(table: str, column: str, ddl: str):
    if not _column_exists(table, column):
        db.execute_sql(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _ensure_schema():
    """Add lightweight columns for existing local databases.

    Peewee creates missing tables, but it does not migrate existing ones. These
    additive checks keep old CazzKB databases usable during the Notebook-style
    transition.
    """
    _ensure_column("document", "source_type", "VARCHAR(255) DEFAULT 'markdown'")
    _ensure_column("document", "summary", "TEXT DEFAULT ''")
    _ensure_column("document", "enabled", "INTEGER DEFAULT 1")


def init_db():
    if DB_PATH != ":memory:":
        os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    db.connect()
    db.create_tables([KnowledgeBase, Document, Chunk, Conversation, Message, Artifact])
    _ensure_schema()
