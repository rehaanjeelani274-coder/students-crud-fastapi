# Students Database CRUD Application

Internship project: Python backend using FastAPI and SQLite. Supports creating, listing/filtering, viewing, updating and deleting student records. Uses dummy records only. Ollama AI extension is optional and not included.

## Requirements
- Python 3.10 or newer
- pip

## Installation and run
Open a terminal in this project folder:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

If Windows recognizes `py` instead of `python`, use `py -m pip ...` and `py -m uvicorn ...`.

Visit http://127.0.0.1:8000/docs to test all endpoints using Swagger UI. Click an endpoint, **Try it out**, fill values, then **Execute**.

## Endpoints
| Method | Route | Purpose |
|---|---|---|
| POST | /students | Create a student |
| GET | /students | List all students; optionally filter with `?name=...` or `?course=...` |
| GET | /students/{student_id} | View one student |
| PATCH | /students/{student_id} | Update specified fields |
| DELETE | /students/{student_id} | Delete a student |

## Example dummy data for POST /students
```json
{
  "name": "Aarav Sample",
  "date_of_birth": "2005-06-15",
  "email": "aarav@example.com",
  "phone": "9876543210",
  "course": "Computer Science",
  "address": "Sample City",
  "enrollment_date": "2024-08-01"
}
```

Example PATCH body: `{"course": "Cyber Security"}`. Use the ID returned by POST in the PATCH/GET/DELETE route. Try `GET /students?course=Cyber` to filter. After restarting the server, GET /students should still return stored records: SQLite persists them in `students.db` (automatically created on first run). Missing IDs return HTTP 404. Invalid input returns HTTP 422. At least one of email or phone is required.

## Architecture
`main.py` defines FastAPI endpoints, validates request bodies with Pydantic, and runs parameterized SQLite queries. A lifespan handler creates the database table if it does not exist. SQLite stores the records locally.

## Submission
Upload `main.py`, `requirements.txt`, and `README.md` to your own GitHub repository. Do not upload `students.db` containing personal data, `.venv`, or passwords. Submit your GitHub repository link to your trainer.
