# Validation Engine

## Overview

The Data Validation Engine is a rule-based validation system that validates structured JSON data against configurable schema definitions and business rules.

The engine validates:

- Schema structure
- Response structure
- Data types
- Allowed values
- Pattern validation
- Minimum value validation
- Maximum value validation
- Maximum length validation
- Dependency rules
- Warning generation

After validation, the engine generates a detailed output containing validation errors, warnings, suggested values (where applicable), and a validation summary.

---

# Project Flow

```text
              input_schema.json
(Field Schema + Validation Rules + Dependency Rules)
                     │
                     │
              response.json
                     │
                     ▼
                validate.py
                     │
                     ▼
                output.json
```

validate.py reads both input_schema.json and response.json, performs all validations, and generates output.json.

---

#  Project Structure

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

# Project Files

## 1. models.py

This file contains the data models, enums, error codes, warning codes, and basic validations used throughout the project.

### Components

#### DependencyOperator

Defines all supported dependency operators.

Supported operators:

- equals
- notEquals
- in
- notIn
- greaterThan
- greaterThanOrEqual
- lessThan
- lessThanOrEqual
- isNull
- isNotNull
- isEmpty
- isNotEmpty

#### ErrorCode

Defines all validation error codes.

Examples:

- INVALID_FIELD_KEY
- INVALID_SCHEMA
- INVALID_TYPE
- INVALID_OPTIONS
- INVALID_FORMAT
- MIN_VALUE_ERROR
- MAX_VALUE_ERROR
- MAX_LENGTH_ERROR
- DEPENDENCY_ERROR
- PYDANTIC_ERROR

#### WarningCode

Defines warning codes.

Examples:

- LOW_CONFIDENCE
- MISSING_FIELD

#### SchemaField

Represents each field defined in the schema.

Each field contains:

- key
- label
- type
- options
- format

#### ResponseField

Represents each field in the response.

Each field contains:

- field_key
- field_label
- value
- is_present
- confidence_score

#### Pydantic Validation

Performs basic validations such as:

- confidence_score must be between **0 and 1**
- value must be **null** when **is_present = false**

---

## 2. input_schema.json

This file contains the complete configuration used by the validation engine.

It has three main sections:

### field_schema

Defines all supported fields.

Each field contains:

- key
- label
- type
- options
- format

### validation_rules

Defines field-level validation rules.

Supported validations:

- Pattern Validation
- Minimum Value Validation
- Maximum Value Validation
- Maximum Length Validation

### dependency_rules

Defines relationships between fields.

Depending on another field's value, a field can be:

- Required
- Hidden
- Cleared

---

## 3. response.json

This file contains the input data to be validated.

Each field contains:

- field_key
- field_label
- value
- is_present
- confidence_score

The validation engine validates this response using the rules defined in **input_schema.json**.

---

## 4. validate.py

This is the main validation engine.

Responsibilities:

- Read input files
- Validate schema
- Validate response
- Execute validation rules
- Execute dependency rules
- Generate warnings
- Generate validation summary
- Generate output.json

---

## 5. output.json

This file contains the final validation result.

It includes:

- is_valid
- errors
- warnings
- summary

---

# Validation Process

### Step 1

Read **input_schema.json**.

### Step 2

Validate the schema.

Checks include:

- Required schema keys
- Duplicate schema fields
- Field types
- Allowed options

### Step 3

Read **response.json**.

### Step 4

Validate the response.

Checks include:

- Required response keys
- Invalid field keys

### Step 5

Perform Pydantic validation.

Checks include:

- Confidence score validation
- Value validation
- is_present validation

### Step 6

Execute validation rules.

Supported validations:

- Pattern Validation
- Minimum Value Validation
- Maximum Value Validation
- Maximum Length Validation

### Step 7

Execute dependency rules.

Supported dependency actions:

- require
- hide
- clearValue

Supported dependency operators:

- equals
- notEquals
- in
- notIn
- greaterThan
- greaterThanOrEqual
- lessThan
- lessThanOrEqual
- isNull
- isNotNull
- isEmpty
- isNotEmpty

### Step 8

Generate warnings.

Supported warnings:

- LOW_CONFIDENCE
- MISSING_FIELD

### Step 9

Generate the validation summary.

The summary includes:

- Total fields
- Passed fields
- Failed fields
- Warning fields
- Duplicate schema fields
- Error summary
- Warning summary

### Step 10

Generate **output.json**.

---

# Supported Validations

The validation engine supports:

- Schema Validation
- Response Validation
- Pattern Validation
- Type Validation
- Enum Validation
- Boolean Validation
- Multi-select Validation
- Minimum Value Validation
- Maximum Value Validation
- Maximum Length Validation
- Dependency Validation
- Pydantic Validation
- Low Confidence Warning
- Missing Field Warning

---

# Output Format

## is_valid

Indicates the final validation result.

- **true** → Validation passed successfully.
- **false** → One or more validation errors were found.

## errors

Contains all validation errors.

Each error includes:

- field_key
- field_label
- error_code
- error
- received
- suggested_value

## warnings

Contains non-blocking issues.

Examples:

- LOW_CONFIDENCE
- MISSING_FIELD

## summary

Provides an overview of the validation results.

Includes:

- total_fields
- passed_fields
- failed_fields
- warning_fields
- duplicate_schema_fields
- error_summary
- warning_summary

---

# How to Run

1. Place **input_schema.json** and **response.json** in the project folder.

2. Run:

```bash
python validate.py
```

3. After execution, the engine generates **output.json**.

---

# Technologies Used

- Python
- Pydantic
- JSON
- Regular Expressions (Regex)

---
