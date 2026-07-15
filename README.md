# Validation Engine

## Overview

The Validation Engine is a Python application that validates AI-extracted response data against a predefined input schema.

It performs multiple validation stages to ensure that the extracted data follows the expected schema, satisfies business rules, and is ready for downstream processing.

The validator checks the structure of both the input schema and the extracted response, validates field values, applies dependency rules, and generates detailed errors, warnings, and summary statistics.

---

# Validation Pipeline

The validation process consists of three major stages:

## 1. Input Schema Validation

Before validating the response, the input schema itself is validated.

This includes:

- Validate top-level schema keys
  - field_schema
  - validation_rules
  - dependency_rules

- Validate field schema
  - Required keys (key, label, type)
  - Supported field types
  - Field options
  - Duplicate schema fields

- Build schema dictionary

Only a valid schema is used for further validation.

---

## 2. Response Validation

After the schema is validated, the extracted response is validated.

This includes:

- Validate response structure
- Validate required response keys
- Validate duplicate response fields
- Validate field keys against the input schema
- Validate enum values
- Validate boolean values
- Validate multi-select values
- Validate response model using Pydantic
- Validate confidence score
- Validate is_present and value relationship

---

## 3. Validation Rules

Each extracted field is validated using configurable validation rules.

Supported validations include:

- Pattern validation
- Minimum value validation
- Maximum value validation

Supported suggestions include:

- Date format suggestion
- Plan number formatting suggestion

---

## 4. Cross Field Validation

Dependency rules are validated after all fields have been processed.

Supported dependency operators:

- equals
- notEquals
- in

Supported dependency actions:

- require
- hide
- clearValue

The validator reports dependency violations without modifying the response.

---

## 5. Warnings

The validator also generates warnings.

Supported warnings:

- LOW_CONFIDENCE
- MISSING_FIELD

---

## Features

The validator supports:

- Input schema validation
- Response validation
- Duplicate schema detection
- Duplicate response detection
- Enum validation
- Boolean validation
- Multi-select validation
- Pattern validation
- Minimum value validation
- Maximum value validation
- Dependency validation
- Pydantic model validation
- Low confidence detection
- Missing field detection
- Suggested values for supported format errors
- Error and warning summary generation

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

- Field schema
- Validation rules
- Dependency rules

### response.json

Contains AI extracted response fields.

---

## Output

The validator generates an `output.json` file containing:

- Validation status
- Validation errors
- Validation warnings
- Validation summary
- Error summary
- Warning summary

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

- SCHEMA_ERROR
- RESPONSE_ERROR
- INVALID_FIELD_KEY
- INVALID_SCHEMA
- INVALID_TYPE
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

Execute:

```bash
python validate.py
```

The validator generates:

```
output.json
```

---

## Use Case

This project validates AI-extracted document data before it is consumed by downstream systems.

It ensures that:

- The input schema is valid
- The extracted response follows the schema
- Field values satisfy business rules
- Cross-field dependencies are respected
- Invalid, missing, or low-confidence data is identified through detailed validation reports