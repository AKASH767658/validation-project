# Validation Engine

## Overview

The Validation Engine is a Python-based application that validates extracted response data against a predefined input schema.

Its purpose is to ensure that every extracted field follows the expected structure, format, allowed values, and business rules before the data is used by downstream systems.

The validator generates detailed errors, warnings, and a summary report to help identify data quality issues.

---

## Features

The validator performs the following checks:

- Validates field keys against the input schema
- Detects duplicate field definitions in the schema
- Validates enum, boolean, and multi-select values
- Validates data formats using configurable validation rules
- Checks minimum and maximum value constraints
- Validates dependency rules between fields
- Detects invalid or missing values
- Generates LOW_CONFIDENCE warnings
- Reports missing fields
- Provides suggested values for supported format errors
- Generates a validation summary with error and warning counts

---

## Project Structure

```
validation_v2/
│
├── data/
│   ├── input_schema.json
│   └── response.json
│
├── models.py
├── validate.py
├── output.json
└── README.md
```

---

## Input Files

### input_schema.json

Contains:

- Field definitions
- Field types
- Allowed options
- Dependency rules
- Validation rules

### response.json

Contains the extracted fields that need to be validated.

---

## Validation Process

The validator performs validation in the following order:

1. Validate field keys
2. Validate enum and boolean options
3. Validate multi-select fields
4. Validate field formats
5. Validate minimum and maximum values
6. Perform dependency validation
7. Generate confidence warnings
8. Generate missing field warnings
9. Generate validation summary

---

## Output

The validator produces an `output.json` file containing:

- Overall validation status
- Validation errors
- Validation warnings
- Summary statistics

Example:

```json
{
    "is_valid": false,
    "errors": [],
    "warnings": [],
    "summary": {}
}
```

---

## Error Codes

- INVALID_FIELD_KEY
- INVALID_OPTIONS
- INVALID_FORMAT
- MIN_VALUE_ERROR
- MAX_VALUE_ERROR
- DEPENDENCY_ERROR
- PYDANTIC_ERROR

---

## Warning Codes

- LOW_CONFIDENCE
- MISSING_FIELD

---

## Requirements

- Python 3.10+
- Pydantic

Install dependencies:

```bash
pip install pydantic
```

---

## Run the Project

Execute the validator:

```bash
python validate.py
```

The validation result will be generated as:

```
output.json
```

---

## Use Case

This project is designed for validating AI-extracted document data before it is processed by downstream applications. It helps ensure that extracted information is complete, correctly formatted, and consistent with the defined business rules.


