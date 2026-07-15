# Database Design

## Overview
This document defines a production-ready PostgreSQL schema for the OCR + RAG document chat system. The actual embedding vectors are stored in FAISS; PostgreSQL stores metadata and references only.

## Design Principles
- UUID primary keys for distributed-safe identity
- Timestamp fields for auditability
- Soft delete support for users, documents, and chat history where appropriate
- Normalized relational structure with clear ownership and foreign keys
- Indexes on frequently queried columns

## Core Tables
- users
- documents
- ocr_text
- chunks
- embedding_metadata
- chat_history

## Relationship Summary
- One user owns many documents and chat sessions
- One document has many OCR text records, chunks, and chat history entries
- One chunk references one embedding metadata record

## Soft Delete Strategy
- Use is_deleted BOOLEAN and deleted_at TIMESTAMP WITH TIME ZONE
- Exclude soft-deleted records from active queries by default

## Recommended Indexes
- Email uniqueness and lookup
- User-to-document and document-to-chat foreign keys
- Status and created_at filtering
- Chunk document and chunk index ordering
- Chat history user/document ordering
