from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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