import json
import re

from pydantic import ValidationError
from models import (
    SchemaField,
    ResponseField,
    DependencyOperator
)
CONFIDENCE_THRESHOLD = 0.90

with open("data/input_schema.json", "r") as file:
    data = json.load(file)

required_keys = {
    "field_schema": False,      # False = should not be empty
    "validation_rules": True,   # True = can be empty
    "dependency_rules": True    # True = can be empty
}

for key, can_be_empty in required_keys.items():

    if key not in data:
        raise ValueError(f"{key} key is missing")

    if not isinstance(data[key], list):
        raise ValueError(f"{key} must be a list")

    if not can_be_empty and len(data[key]) == 0:
        raise ValueError(f"{key} must not be empty")

field_schema = data["field_schema"]
validation_rules = data["validation_rules"]
dependency_rules = data["dependency_rules"]

# -------------------------
# validation rules dict
# -------------------------
rules_dict = {}

for rule in validation_rules:
    rules_dict[rule["field"]] = rule["rules"]


# -------------------------
# load response.json
# -------------------------
with open("data/response.json", "r") as file:
    response_data = json.load(file)


errors = []
warnings = []
response_keys = []
invalid_fields = set()
duplicate_response_fields = []






#HELPER  FUN
def validate_required_keys(item):

    for key in ["key", "label", "type"]:

        if key not in item:
            return f"{key} is missing."

    return None


def validate_schema_type(item):

    valid_types = [
        "text",
        "enum_single",
        "enum_multi",
        "boolean"
    ]

    if item["type"] not in valid_types:
        return f"Unsupported type: {item['type']}"

    return None


def validate_options(item):

    field_type = item["type"]
    options = item.get("options")

    if field_type in ["enum_single", "enum_multi"]:

        if not isinstance(options, list) or len(options) == 0:
            return "Options must be a non-empty list."

    elif field_type == "boolean":

        if not isinstance(options, list) or len(options) == 0:
            return "Boolean options must be a non-empty list."

    elif field_type == "text":

        if options is not None:
            return "Options must be null."

    return None

def validate_response(response_data):

    if "extracted_fields" not in response_data:
        return "extracted_fields key is missing."

    if not isinstance(response_data["extracted_fields"], list):
        return "extracted_fields must be a list."

    if len(response_data["extracted_fields"]) == 0:
        return "extracted_fields must not be empty."

    return None

def validate_response_keys(item):

    required_keys = [
        "field_key",
        "field_label",
        "value",
        "is_present",
        "confidence_score"
    ]

    for key in required_keys:

        if key not in item:
            return f"{key} is missing."

    return None

def add_low_confidence_warning(
    warnings,
    field_key,
    field_label,
    confidence_score
):

    if confidence_score < CONFIDENCE_THRESHOLD:

        warnings.append({
            "field_key": field_key,
            "field_label": field_label,
            "warning_code": "LOW_CONFIDENCE",
            "warning": "Low confidence score",
            "received": confidence_score
        })

def check_condition(actual_value, operator, expected_value):

    if operator == DependencyOperator.EQUALS:
        return actual_value == expected_value

    elif operator == DependencyOperator.NOT_EQUALS:
        return actual_value != expected_value

    elif operator == DependencyOperator.IN:
        return actual_value in expected_value

    return False


def process_require_action(
    action,
    response_map,
    schema_dict,
    errors,
    dep_rule
):

    for child_field in action["fields"]:

        child_value = response_map.get(child_field)

        if (
            child_field not in response_map
            or child_value is None
            or str(child_value).strip() == ""
        ):

            errors.append({
                "field_key": child_field,
                "field_label": schema_dict[child_field].label,
                "error_code": "DEPENDENCY_ERROR",
                "error": dep_rule.get(
                    "messages",
                    {}
                ).get(
                    child_field,
                    "Dependency validation failed."
                ),
                "received": child_value,
                "suggested_value": None
            })


def process_hide_clear_action(
    action,
    response_map,
    schema_dict,
    errors,
    dependency_checked,
    parent_field
):

    for child_field in action["fields"]:

        child_value = response_map.get(child_field)

        check_key = parent_field + "_" + child_field

        if (
            child_value is not None
            and check_key not in dependency_checked
        ):

            dependency_checked.add(check_key)

            errors.append({
                "field_key": child_field,
                "field_label": schema_dict[child_field].label,
                "error_code": "DEPENDENCY_ERROR",
                "error": "Field should not be present because parent condition is not satisfied.",
                "received": child_value,
                "suggested_value": None
            })


def validate_pattern(
    value,
    field_key,
    field_label,
    rule,
    errors,
    invalid_fields
):

    suggested_value = None

    pattern = rule["value"]

    if not re.match(pattern, value):

        if "-" in value:
            year, month, day = value.split("-")
            suggested_value = f"{month}/{day}/{year}"

        if field_key == "planNumber":

            suggested_value = value.zfill(3)

        elif field_key == "planEffectiveDate":

            parts = value.split("/")

            if len(parts) == 3:

                suggested_value = (
                    parts[0].zfill(2)
                    + "/"
                    + parts[1].zfill(2)
                    + "/"
                    + parts[2]
                )

        errors.append({

            "field_key": field_key,
            "field_label": field_label,
            "error_code": "INVALID_FORMAT",
            "error": rule["message"],
            "received": value,
            "suggested_value": suggested_value

        })

        invalid_fields.add(field_key)

def validate_min(
    value,
    field_key,
    field_label,
    rule,
    errors,
    invalid_fields
):

    try:

        if isinstance(value, (int, float)):
            num = float(value)
        else:
            num = float(str(value).replace("%", ""))

        if num < rule["value"]:

            errors.append({

                "field_key": field_key,

                "field_label": field_label,

                "error_code": "MIN_VALUE_ERROR",

                "error": rule["message"],

                "received": value,

                "suggested_value": None

            })

            invalid_fields.add(field_key)

    except (ValueError, TypeError):
        pass

def validate_max(
    value,
    field_key,
    field_label,
    rule,
    errors,
    invalid_fields
):

    try:

        if isinstance(value, (int, float)):
            num = float(value)
        else:
            num = float(str(value).replace("%", ""))

        if num > rule["value"]:

            errors.append({

                "field_key": field_key,

                "field_label": field_label,

                "error_code": "MAX_VALUE_ERROR",

                "error": rule["message"],

                "received": value,

                "suggested_value": None

            })

            invalid_fields.add(field_key)

    except (ValueError, TypeError):
        pass

error = validate_response(response_data)

if error:
    errors.append({
        "error_code": "RESPONSE_ERROR",
        "error": error
    })
# -------------------------
# schema dictionary
# -------------------------
schema_dict = {}
duplicate_fields = []

for item in field_schema:
    error = validate_required_keys(item)

    if error:
        errors.append({
            "error_code": "SCHEMA_ERROR",
            "error": error
        })
        continue

    error = validate_schema_type(item)

    if error:
        errors.append({
            "field_key": item["key"],
            "error_code": "INVALID_TYPE",
            "error": error
        })
        continue

    error = validate_options(item)

    if error:
        errors.append({
            "field_key": item["key"],
            "error_code": "INVALID_SCHEMA",
            "error": error
        })
        continue

    schema = SchemaField(
        **item
    )
    if schema.key in schema_dict:

        duplicate_fields.append(schema.key)
    else:
        schema_dict[
        schema.key
    ] = schema
print("Duplicate fields:", duplicate_fields)


# -------------------------
# validation loop
# -------------------------
for item in response_data[ 
    "extracted_fields"
]:
    error = validate_response_keys(item)

    if error:
        errors.append({
            "error_code": "RESPONSE_ERROR",
            "error": error
        })
        continue

    field_key = item[
        "field_key"
    ]

    field_label = item[
        "field_label"
    ]

    value = item[
        "value"
    ]

    if field_key in response_keys:
        duplicate_response_fields.append(field_key)
    else:
        response_keys.append(field_key)

    


    # -------------------------
    # invalid field_key
    # -------------------------
    if field_key not in schema_dict:

        errors.append({

            "field_key": field_key,

            "field_label": None,

            "error_code": "INVALID_FIELD_KEY",

            "error":
            "field_key not found in input_schema.json schema",

            "received": field_key,

            "suggested_value": None
        })

        invalid_fields.add(
            field_key
        )

        continue

    schema = schema_dict[
        field_key
    ]
    
         # -------------------------
# -------------------------
# schema options validation
# -------------------------

    if schema.options is not None:

    # enum_single / boolean
     if schema.type in ["enum_single", "boolean"]:

        if value not in schema.options:

            errors.append({
                "field_key": field_key,
                "field_label": field_label,
                "error_code": "INVALID_OPTIONS",
                "error": f"{field_label} contains an invalid option.",
                "received": value,
                "suggested_value": None
            })
            

            invalid_fields.add(field_key)

            add_low_confidence_warning(
    warnings,
    field_key,
    field_label,
    item["confidence_score"]
)
            continue

    # enum_multi
     elif schema.type == "enum_multi":
       
        
        if not isinstance(value, list):

            errors.append({
                "field_key": field_key,
                "field_label": field_label,
                "error_code": "INVALID_TYPE",
                "error": f"{field_label}  must be a list of values.",
                "received": value,
                "suggested_value": None
            })

            invalid_fields.add(field_key)
            add_low_confidence_warning(
    warnings,
    field_key,
    field_label,
    item["confidence_score"]
)
            
            continue
        invalid = False
        for option in value:

            if option not in schema.options:
                invalid = True
                break
        if invalid:        

                errors.append({
                    "field_key": field_key,
                    "field_label": field_label,
                    "error_code": "INVALID_OPTIONS",
                    "error": f"{field_label} contains an invalid option.",
                    "received": value,
                    "suggested_value": None
                })

                invalid_fields.add(field_key)
                add_low_confidence_warning(
    warnings,
    field_key,
    field_label,
    item["confidence_score"]
)

                continue
                

    # -------------------------
    # low confidence warning
    
    
    
    # -------------------------
    add_low_confidence_warning(
    warnings,
    field_key,
    field_label,
    item["confidence_score"]
)


    # ------------------ -------
    # pydantic validation
    # -------------------------
    try:

        ResponseField(

            **item,

            schema=schema
        )

    except ValidationError as e:

        errors.append({

            "field_key": field_key,

            "field_label": field_label,

            "error_code":
            "PYDANTIC_ERROR",

            "error": str(e),

            "received": value,

            "suggested_value": None
        })

        invalid_fields.add(
            field_key
        )
        add_low_confidence_warning(
    warnings,
    field_key,
    field_label,
    item["confidence_score"]
)

        continue
    # -------------------------
    # validation_rules
    # -------------------------
    if field_key in rules_dict:

        field_rules = rules_dict[
            field_key
        ]

        for rule in field_rules:

            rule_type = rule[
                "type"
            ]

            suggested_value = None


            # -------------------------
            # pattern validation
            # -------------------------
            if rule_type == "pattern":
                validate_pattern(
                    value,
                    field_key,
                    field_label,
                    rule,
                    errors,
                    invalid_fields
                    )
            # -------------------------
            # min validation
            # -------------------------
            elif rule_type == "min":
                validate_min(
        value,
        field_key,
        field_label,
        rule,
        errors,
        invalid_fields
    )


            # -------------------------
            # max validation
            # -------------------------
            elif rule_type == "max":
                validate_max(
        value,
        field_key,
        field_label,
        rule,
        errors,
        invalid_fields
    )
            
# -------------------------
# create response map
# -------------------------
response_map = {}

for item in response_data[
    "extracted_fields"
]:

    response_map[
        item["field_key"]
    ] = item["value"]


# -------------------------
# dependency validation
# -------------------------
dependency_checked = set()

for dep_rule in dependency_rules:

    when = dep_rule["when"]

    parent_field = when["field"]

    operator = when["operator"]

    expected_value = when["value"]


    # skip if parent already invalid
    if parent_field in invalid_fields:
        continue


    actual_value = response_map.get(
        parent_field
    )

    condition_met = check_condition(
    actual_value,
    operator,
    expected_value
)


    # -------------------------
    # THEN actions
    # parent valid -> child required
    # -------------------------
    if condition_met:

        for action in dep_rule["then"]:
            if action["action"] == "require":
                process_require_action(
                    action,
                    response_map,
                    schema_dict,
                    errors,
                    dep_rule
                 )


    # -------------------------
    # ELSE actions
    # parent not applicable
    # child should NOT exist
    # -------------------------
    else:

        for action in dep_rule["else"]:

            action_type = action["action"]

            if action_type in [
                "hide",
                "clearValue"
            ]:

                process_hide_clear_action(
                    action,
                    response_map,
                    schema_dict,
                    errors,
                    dependency_checked,
                    parent_field
                    )


# -------------------------
# missing field warning
# -------------------------
for key in schema_dict:

    if key not in response_keys:

        warnings.append({

            "field_key": key,

            "field_label":
            schema_dict[key].label,

            "warning_code":
            "MISSING_FIELD",

            "warning":
            "Field missing in response",

            "received": None
        })


# -------------------------
# summary
# -------------------------
total_fields = len(
    field_schema
)

failed_field_names = set()

for err in errors:

    failed_field_names.add(
        err["field_key"]
    )

failed_fields = len(
    failed_field_names
)

warning_fields = len(
    warnings
)

passed_fields = (
    total_fields
    - failed_fields
)


# -------------------------
# error summary
# -------------------------
error_summary = {}

for err in errors:

    code = err["error_code"]

    if code not in error_summary:

        error_summary[
            code
        ] = 1

    else:

        error_summary[
            code
        ] += 1

# -------------------------
# warning summary
# -------------------------
warning_summary = {}

for warn in warnings:

    code = warn["warning_code"]

    if code not in warning_summary:

        warning_summary[
            code
        ] = 1

    else:

        warning_summary[
            code
        ] += 1

# final output
# -------------------------
result = {

    "is_valid":
    len(errors) == 0,

    "errors":
    errors,

    "warnings":
    warnings,

    "summary": {

        "total_fields":
        total_fields,

        "passed_fields":
        passed_fields,

        "failed_fields":
        failed_fields,

        "warning_fields":
        warning_fields,
       "duplicate_schema_fields": list(set(duplicate_fields)),

        "error_summary":
        error_summary,

        "warning_summary":
    warning_summary
    }
}

print(
    result
)
with open(
    "output.json",
    "w"
) as file:

    json.dump(

        result,

        file,

        indent=4
    )