from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases
import csv
import io

# Database configuration
DATABASE_URL = "sqlite:///./test.db"
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model for operations
class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, index=True)
    result = Column(Float, index=True)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# FastAPI app instance
app = FastAPI()

# Pydantic model for operation request
class OperationRequest(BaseModel):
    operation: str

# Pydantic model for operation response
class OperationResponse(BaseModel):
    id: int
    operation: str
    result: float

# Route to calculate RPN operation and store in database
@app.post("/calculate/", response_model=OperationResponse)
async def calculate(operation_req: OperationRequest):
    operation = operation_req.operation.strip()
    try:
        result = eval(operation)
        db = SessionLocal()
        db_operation = Operation(operation=operation, result=result)
        db.add(db_operation)
        db.commit()
        db.refresh(db_operation)
        db.close()
        return {"id": db_operation.id, "operation": operation, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid operation: {str(e)}")

# Route to export operations to CSV file
@app.get("/export/csv/")
async def export_csv():
    db = SessionLocal()
    operations = db.query(Operation).all()
    db.close()

    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(["id", "operation", "result"])
    for op in operations:
        csv_writer.writerow([op.id, op.operation, op.result])

    return {"csv_data": output.getvalue()}

# Connect to database on startup
@app.on_event("startup")
async def startup():
    await database.connect()

# Disconnect from database on shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Run the FastAPI server with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
