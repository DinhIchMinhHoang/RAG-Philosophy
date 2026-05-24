import sys
import os
from sqlalchemy import text
sys.path.insert(0, r'd:\RAG-Philosophy')
from backend.app.database import SessionLocal
from backend.app.models import ExcelTableRecord

db = SessionLocal()
records = db.query(ExcelTableRecord).filter(ExcelTableRecord.user_id == 'btndung06@gmail.com').all()
for r in records:
    try:
        sql = f'SELECT * FROM "{r.table_name}" WHERE search_text ILIKE \'%anh%\' AND search_text ILIKE \'%b2%\''
        res = db.execute(text(sql)).fetchall()
        if res:
            print('FOUND in', r.table_name)
            print(f'Count: {len(res)}')
    except Exception as e:
        print(f"Error on {r.table_name}: {e}")
