from __future__ import annotations

from typing import Final

from qdrant_client.http import models

from agent.services.rag.sources.base import PayloadIndexDefinition, RagSourceDefinition
from agent.services.rag.sources.post.source import POST_SOURCE


RAG_SOURCE_DEFINITIONS: Final[tuple[RagSourceDefinition, ...]] = (POST_SOURCE,)


def validate_rag_sources(
    sources: tuple[RagSourceDefinition, ...],
) -> tuple[RagSourceDefinition, ...]:
    source_types: set[str] = set()
    index_by_field: dict[str, PayloadIndexDefinition] = {}

    for source in sources:
        if source.source_type in source_types:
            raise ValueError(
                f"중복된 RAG source type이 등록되었습니다. sourceType={source.source_type}"
            )
        source_types.add(source.source_type)

        indexed_fields = {index.field_name for index in source.payload_indexes}
        if "sourceType" not in indexed_fields:
            raise ValueError(
                f"RAG source는 sourceType payload index를 정의해야 합니다. sourceType={source.source_type}"
            )

        for field_name in source.filter_field_names:
            if field_name not in indexed_fields:
                raise ValueError(
                    f"RAG source filter field에는 payload index가 있어야 합니다. "
                    f"sourceType={source.source_type} field={field_name}"
                )

        for index in source.payload_indexes:
            if index.field_name == "sourceType" and index.is_tenant:
                raise ValueError(
                    "sourceType은 tenant partition이 아니므로 is_tenant=true를 사용하면 안 됩니다."
                )

            previous = index_by_field.get(index.field_name)
            if previous is not None and (
                previous.field_schema != index.field_schema or previous.is_tenant != index.is_tenant
            ):
                raise ValueError(f"payload index 정의가 충돌합니다. field={index.field_name}")
            index_by_field[index.field_name] = index

    return sources


RAG_SOURCES: Final[tuple[RagSourceDefinition, ...]] = validate_rag_sources(RAG_SOURCE_DEFINITIONS)


def payload_indexes_for_registered_sources() -> list[PayloadIndexDefinition]:
    indexes: dict[str, PayloadIndexDefinition] = {}
    for source in RAG_SOURCES:
        for index in source.payload_indexes:
            indexes[index.field_name] = index
    return list(indexes.values())


def qdrant_field_schema(index: PayloadIndexDefinition) -> models.PayloadSchemaType:
    return index.field_schema
