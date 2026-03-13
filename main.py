from fastapi import FastAPI, status, HTTPException, Depends
from google.cloud import bigquery
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Dependency method to provide a BigQuery client
# This will be used by the other endpoints where a database connection is necessary
def get_bq_client():
    # client automatically uses Cloud Run's service account credentials
    client = bigquery.Client()
    try:
        yield client
    finally:
        client.close()

app = FastAPI()

# --- PART 3: CUSTOM ERROR HANDLING ---
# This overrides the default FastAPI 422 error to give the "friendly" message requested.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "All arguments must be valid numbers."},
    )

@app.get("/", status_code=200)
def read_root():
    """Health check endpoint to verify the API is live."""
    return {"status": "healthy"}

# --- PART 1: REQUIRED ENDPOINTS ---

@app.get("/add/{a}/{b}")
def add(a: float, b: float):
    """Adds two numbers and returns the operation details and result."""
    return {"operation": "add", "a": a, "b": b, "result": a + b}

@app.get("/subtract/{a}/{b}")
def subtract(a: float, b: float):
    """Subtracts b from a and returns the operation details and result."""
    return {"operation": "subtract", "a": a, "b": b, "result": a - b}

@app.get("/multiply/{a}/{b}")
def multiply(a: float, b: float):
    """Multiplies two numbers and returns the operation details and result."""
    return {"operation": "multiply", "a": a, "b": b, "result": a * b}

@app.get("/divide/{a}/{b}")
def divide(a: float, b: float):
    """Divides a by b. Returns a 422 error if b is zero."""
    if b == 0:
        return JSONResponse(
            status_code=422,
            content={"error": "Division by zero is not allowed. Please provide a non-zero value for b."}
        )
    return {"operation": "divide", "a": a, "b": b, "result": a / b}

# --- PART 2: CUSTOM ENDPOINTS ---

@app.get("/average/{a}/{b}/{c}")
def average(a: float, b: float, c: float):
    """Calculates the average of three numbers to satisfy the >2 parameter requirement."""
    return {"operation": "average", "a": a, "b": b, "c": c, "result": (a + b + c) / 3}

@app.get("/power/{base}/{exponent}")
def power(base: float, exponent: float):
    """Calculates the base raised to the power of the exponent."""
    return {"operation": "power", "base": base, "exponent": exponent, "result": base ** exponent}

@app.get("/tip/{total}/{percentage}")
def calculate_tip(total: float, percentage: float):
    """Calculates the tip amount based on a bill total and a tip percentage."""
    if total < 0 or percentage < 0:
        return JSONResponse(status_code=422, content={"error": "Total and percentage must be positive values."})
    result = total * (percentage / 100)
    return {"operation": "tip", "total": total, "percentage": percentage, "result": result}

@app.get("/dbwritetest", status_code=200)

def dbwritetest(bq: bigquery.Client = Depends(get_bq_client)):
    """
    Writes a simple test row to a BigQuery table.

    Uses the `get_bq_client` dependency method to establish a connection to BigQuery.
    """
    # Define a Python list of objects that will become rows in the database table
    # In this instance, there is only a single object in the list
    row_to_insert = [
        {
            "endpoint": "/dbwritetest",
            "result": "Success",
            "status_code": 200
        }
    ]
    
    # Use the BigQuery interface to write our data to the table
    # If there are errors, store them in a list called `errors`
    # YOU MUST UPDATE YOUR PROJECT AND DATASET NAME BELOW BEFORE THIS WILL WORK!!!
    errors = bq.insert_rows_json("project-ad28b983-985e-4f90-b15.calculator.api_logs", row_to_insert)

    # If there were any errors, raise an HTTPException to inform the user
    if errors:
        # Log the full error to your Cloud Run logs for debugging
        print(f"BigQuery Insert Errors: {errors}")
        
        # Raise an exception to the API user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to log data to BigQuery",
                "errors": errors  # Optional: return specific BQ error details
            }
        )

    # If there were NOT any errors, send a friendly response message to the API caller
    return {"message": "Log entry created successfully"}