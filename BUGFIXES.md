# Bug Fixes - Chunk Saving Issue

## Overview
Chunks were not being saved to the database correctly due to multiple issues in the data processing pipeline.

---

## Issue 1: Async Function Not Awaited

### Location: `src/routes/file.py` (Line 70)

### Original Code:
```python
p_cont.insert_chunks(request,file_chunks)
return file_chunks
```

### Problem:
The `insert_chunks()` method is async but was never awaited, causing the database insert operation to silently fail.

### Fixed Code:
```python
chunks_to_save = p_cont.prepare_chunks_for_db(file_chunks, project_id)
inserted_count = await p_cont.insert_chunks(request, chunks_to_save)
return {"chunks_count": inserted_count, "chunks": chunks_to_save}
```

### Reason:
- The async coroutine was created but never executed
- Added `await` to properly execute the database insert operation

---

## Issue 2: Type Mismatch - LangChain Documents vs DataChunk Models

### Location: `src/controllers/ProccessController.py`

### Problem:
The `insert_chunks` method received LangChain `Document` objects but the repository expected `DataChunk` Pydantic models with specific fields.

### Solution:
Added new method `prepare_chunks_for_db()` to convert LangChain Documents to DataChunk Pydantic models:

```python
def prepare_chunks_for_db(self, chunks: list, project_id: str) -> list[DataChunk]:
    from langchain_core.documents.base import Document

    data_chunks = []
    for idx, chunk in enumerate(chunks):
        if isinstance(chunk, Document):
            data_chunk = DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=idx + 1,
                chunk_project_id=ObjectId(project_id)
            )
            data_chunks.append(data_chunk)
    return data_chunks
```

### Reason:
- LangChain Documents have `page_content` and `metadata` attributes
- DataChunk model requires `chunk_text`, `chunk_metadata`, `chunk_order`, and `chunk_project_id`
- Needed to convert types before saving to database

---

## Issue 3: Wrong Return Type in Repository

### Location: `src/models/repos/data_chunk_repo.py` (Line 24-36)

### Original Code:
```python
async def find_one_by_id(self, chunk_id: str):
    # ...
    project = Project(**result)
    project.id = id
    return project.model_dump(by_alias=True)
```

### Problem:
Copy-paste error - returning `Project` object instead of `DataChunk`.

### Fixed Code:
```python
async def find_one_by_id(self, chunk_id: str):
    # ...
    data_chunk = DataChunk(**result)
    return data_chunk.model_dump(by_alias=True)
```

### Reason:
- The method was returning wrong model type
- This would cause issues when fetching chunks

---

## Issue 4: Missing by_alias=True in Bulk Insert

### Location: `src/models/repos/data_chunk_repo.py` (Line 20)

### Original Code:
```python
operations = [InsertOne(chunk.model_dump()) for chunk in batch]
```

### Problem:
`model_dump()` without `by_alias=True` doesn't properly map the `_id` field alias in MongoDB.

### Fixed Code:
```python
operations = [
    InsertOne({k: v for k, v in chunk.model_dump(by_alias=True).items() if v is not None})
    for chunk in batch
]
```

### Reason:
- Pydantic's `by_alias=True` ensures field names match MongoDB's expected format
- Without it, the `_id` field from the model (aliased from `id`) wouldn't be correctly serialized
- Filter out `None` values to avoid MongoDB duplicate key error with `_id: null`

---

## Issue 5: Project ID Not Converted to MongoDB ObjectId

### Location: `src/routes/file.py` (Line 63)

### Problem:
The process endpoint received user-friendly project_id (e.g., "test456") but needed MongoDB ObjectId for the chunk.

### Fixed Code:
```python
project_obj = await prj_cont.find_project(request, project_id)
if not project_obj:
    return JSONResponse(...)
mongo_project_id = project_obj["_id"]
# Use mongo_project_id when creating chunks
```

### Reason:
- The DataChunk model requires `chunk_project_id` as MongoDB ObjectId
- User passes human-readable project_id, needed to look up the actual ObjectId

---

## Issue 6: JSON Serialization Error with ObjectId

### Location: `src/routes/file.py` (Line 82)

### Problem:
Returning chunks directly in response caused Pydantic serialization error because ObjectId is not JSON serializable.

### Fixed Code:
```python
return {"chunks_count": inserted_count, "message": "Chunks saved successfully"}
```

### Reason:
- bson ObjectId cannot be serialized to JSON by FastAPI
- Simplified response to just return count and status message

---

## Summary of Changes

| File | Issue | Fix |
|------|-------|-----|
| `src/routes/file.py` | Async function not awaited | Added `await` and conversion logic |
| `src/controllers/ProccessController.py` | Type mismatch | Added `prepare_chunks_for_db()` method |
| `src/models/repos/data_chunk_repo.py` | Wrong return type | Changed to return `DataChunk` |
| `src/models/repos/data_chunk_repo.py` | Missing by_alias & null _id | Added `by_alias=True` and filter None values |
| `src/routes/file.py` | Project ID not converted | Lookup project to get MongoDB ObjectId |
| `src/routes/file.py` | JSON serialization error | Simplified response to avoid ObjectId in JSON |

---

## Testing

To verify the fixes:
1. Upload a PDF file to a project
2. Call the `/api/v1/data/process/{project_id}` endpoint
3. Check MongoDB `chunks` collection for saved documents
4. Verify each chunk has: `chunk_text`, `chunk_metadata`, `chunk_order`, `chunk_project_id`

### Test Results
```
curl -X POST "http://localhost:8000/api/v1/data/process/test456" \
  -H "Content-Type: application/json" \
  -d '{"file_name": "072fdef9a8ddda84.pdf", "chunk_size": 512, "overlap_size": 200}'

# Result:
{"chunks_count":52,"message":"Chunks saved successfully"}
```

### Database Verification
```javascript
db.chunks.find({chunk_project_id: ObjectId('6a01b57634339516bec818a9')})
// Returns 52 chunks with proper _id, chunk_text, chunk_metadata, chunk_order
```

---

## Issue 7: Bitwise OR Instead of Logical OR

### Location: `src/routes/project.py` (Line 47)

### Original Code:
```python
if (result is None | total_pages == 0):
```

### Problem:
Used bitwise OR (`|`) instead of logical OR (`or`), causing type error.

### Fixed Code:
```python
if result is None or total_pages == 0:
```

### Reason:
- `None | 0` raises TypeError in Python
- Must use `or` for logical operations

---

## Issue 8: Missing Request Parameter in Controller Call

### Location: `src/routes/project.py` (Line 40)

### Original Code:
```python
result, total_pages = await projectController.find_all_projects(page, limit)
```

### Problem:
Controller method expects `req` parameter but was not passed.

### Fixed Code:
```python
result, total_pages = await projectController.find_all_projects(req, page, limit)
```

---

## Issue 9: Delete/Update Used project_id as MongoDB ObjectId

### Location: `src/controllers/ProjectController.py`

### Problem:
Delete and update methods expected MongoDB ObjectId but users passed human-readable project_id.

### Fixed Code:
```python
async def update_project(self, req: Request, project_id: str, update_data: Project):
    project_repo = ProjectRepository(req.app.db_client)
    project = await project_repo.find_one_by_project_id(project_id)
    if not project:
        return None
    mongo_id = project["_id"]
    return await project_repo.update_one_by_id(mongo_id, update_data)

async def delete_project(self, req: Request, project_id: str):
    project_repo = ProjectRepository(req.app.db_client)
    project = await project_repo.find_one_by_project_id(project_id)
    if not project:
        return None
    mongo_id = project["_id"]
    return await project_repo.delete_one_by_id(mongo_id)
```

### Reason:
- Need to first look up project by project_id to get MongoDB ObjectId
- Then use ObjectId for update/delete operations

---

## Issue 10: Missing Error Handling for None Result

### Location: `src/routes/project.py`

### Problem:
Delete and update routes didn't handle case when project lookup returns None.

### Fixed Code:
```python
if result is None:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Project Not Found!"},
    )
```

---

## Issue 11: Remove Mockup Routes from Swagger

### Location: `src/main.py` and `src/routes/base.py`

### Changes:
- Removed `base_router` import and registration
- Removed `/api/v1/` welcome endpoint
- Fixed home endpoint message to show API info

### Fixed Code:
```python
app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API",
    version="1.0.0"
)
app.include_router(project.project_router)
app.include_router(file.base_router)

@app.get("/")
async def root():
    return {
        "message": "RAG API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
```

---

## Summary of All Changes

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `src/routes/file.py` | Async function not awaited | Added `await` |
| 2 | `src/controllers/ProccessController.py` | Type mismatch | Added `prepare_chunks_for_db()` |
| 3 | `src/models/repos/data_chunk_repo.py` | Wrong return type | Return `DataChunk` |
| 4 | `src/models/repos/data_chunk_repo.py` | Missing by_alias & null _id | Added filtering |
| 5 | `src/routes/file.py` | Project ID not converted | Lookup project |
| 6 | `src/routes/file.py` | JSON serialization error | Simplified response |
| 7 | `src/routes/project.py` | Bitwise OR (`\|`) | Changed to `or` |
| 8 | `src/routes/project.py` | Missing `req` param | Added `req` |
| 9 | `src/controllers/ProjectController.py` | Delete/Update wrong param | Lookup project first |
| 10 | `src/routes/project.py` | No None handling | Added None check |
| 11 | `src/main.py` | Mockup routes | Removed base router |
| 12 | `src/controllers/ProccessController.py` | File loader throws exception | Added try-catch to return None |
| 13 | `src/routes/file.py` | File not found causes crash | Added None check for file_content |