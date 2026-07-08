import json
import re

from pydantic import ValidationError
from models import SchemaField, ResponseField


# -------------------------
# load demo.json
# -------------------------
with open("data/input_schema.json", "r") as file:
    data = json.load(file)

field_schema = data["field_schema"]
dependency_rules = data["dependency_rules"]
validation_rules = data["validation_rules"]


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


# -------------------------
# schema dictionary
# -------------------------
schema_dict = {}

for item in field_schema:

    schema = SchemaField(
        **item
    )

    schema_dict[
        schema.key
    ] = schema


errors = []
warnings = []
response_keys = []
invalid_fields = set()


# -------------------------
# validation loop
# -------------------------
for item in response_data[
    "extracted_fields"
]:

    field_key = item[
        "field_key"
    ]

    field_label = item[
        "field_label"
    ]

    value = item[
        "value"
    ]

    response_keys.append(
        field_key
    )


    # -------------------------
    # invalid field_key
    # -------------------------
    if field_key not in schema_dict:

        errors.append({

            "field_key": field_key,

            "field_label": None,

            "error_code": "INVALID_FIELD_KEY",

            "error":
            "field_key not found in demo.json schema",

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
# schema options validation
# -------------------------
    if schema.options is not None:

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

        continue

          


    # -------------------------
    # low confidence warning
    
    
    
    # -------------------------
    if item[
        "confidence_score"
    ] < 0.90:

        warnings.append({

            "field_key": field_key,

            "field_label": field_label,

            "warning_code":
            "LOW_CONFIDENCE",

            "warning":
            "Low confidence score",

            "received":
            item["confidence_score"]
        })


    # -------------------------
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

                pattern = rule[
                    "value"
                ]

                if not re.match(
                    pattern,
                    value
                ):

                    # safe suggestion only
                    if field_key == "planNumber":

                        suggested_value = (
                            value.zfill(3)
                        )

                    elif field_key == "planEffectiveDate":

                        parts = value.split(
                            "/"
                        )

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

                        "error_code":
                        "INVALID_FORMAT",

                        "error":
                        rule["message"],

                        "received": value,

                        "suggested_value":
                        suggested_value
                    })

                    invalid_fields.add(
                        field_key
                    )


            # -------------------------
            # min validation
            # -------------------------
            elif rule_type == "min":

                try:

                    num = float(

                        value.replace(
                            "%",
                            ""
                        )
                    )

                    if num < rule[
                        "value"
                    ]:

                        errors.append({

                            "field_key": field_key,

                            "field_label": field_label,

                            "error_code":
                            "MIN_VALUE_ERROR",

                            "error":
                            rule["message"],

                            "received": value,

                            "suggested_value": None
                        })

                        invalid_fields.add(
                            field_key
                        )

                except:
                    pass


            # -------------------------
            # max validation
            # -------------------------
            elif rule_type == "max":

                try:

                    num = float(

                        value.replace(
                            "%",
                            ""
                        )
                    )

                    if num > rule[
                        "value"
                    ]:

                        errors.append({

                            "field_key": field_key,

                            "field_label": field_label,

                            "error_code":
                            "MAX_VALUE_ERROR",

                            "error":
                            rule["message"],

                            "received": value,

                            "suggested_value": None
                        })

                        invalid_fields.add(
                            field_key
                        )

                except:
                    pass


            
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

    condition_met = False


    # operators
    if operator == "equals":

        if actual_value == expected_value:
            condition_met = True


    elif operator == "notEquals":

        if actual_value != expected_value:
            condition_met = True


    elif operator == "in":

        if actual_value in expected_value:
            condition_met = True


    # -------------------------
    # THEN actions
    # parent valid -> child required
    # -------------------------
    if condition_met:

        for action in dep_rule["then"]:

            if action["action"] == "require":

                for child_field in action["fields"]:

                    child_value = response_map.get(
                        child_field
                    )

                    if (

                        child_field not in response_map

                        or child_value is None

                        or str(child_value).strip() == ""
                    ):

                        errors.append({

                            "field_key": child_field,

                            "field_label":
                            schema_dict[
                                child_field
                            ].label,

                            "error_code":
                            "DEPENDENCY_ERROR",

                            "error":
                            dep_rule.get(
                                "messages",
                                {}
                            ).get(
                                child_field,
                                "Dependency validation failed."
                            ),

                            "received":
                            child_value,

                            "suggested_value": None
                        })


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

                for child_field in action["fields"]:

                    child_value = response_map.get(
                        child_field
                    )

                    # avoid duplicate dependency errors
                    check_key = (
                        parent_field
                        + "_"
                        + child_field
                    )

                    if (

                        child_value is not None

                        and check_key
                        not in dependency_checked
                    ):

                        dependency_checked.add(
                            check_key
                        )

                        errors.append({

                            "field_key": child_field,

                            "field_label":
                            schema_dict[
                                child_field
                            ].label,

                            "error_code":
                            "DEPENDENCY_ERROR",

                            "error":
                            "Field should not be present because parent condition is not satisfied.",

                            "received":
                            child_value,

                            "suggested_value": None
                        })


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

# -------------------------
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