import datetime
from peewee import (
    SqliteDatabase, Model, CharField, TextField, IntegerField,
    FloatField, BooleanField, DateTimeField, ForeignKeyField,
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


def init_db():
    if DB_PATH != ":memory:":
        os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    db.connect()
    db.create_tables([KnowledgeBase, Document, Chunk, Conversation, Message])
