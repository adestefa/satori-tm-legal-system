# Guide to the Hydrated JSON Schema (v3.0)

**Date:** 2025-07-04

## 1. Overview

This document provides a comprehensive guide to the `HydratedJSON` schema, which is the single source of truth for the data structure passed between the Tiger and Monkey services. Adherence to this schema is critical for the successful generation of court-ready legal documents.

The schema is defined in `shared-schema/satori_schema/hydrated_json_schema.py` using Pydantic models. This guide explains each component of the schema, with a focus on required fields and correct data types.

## 2. Top-Level Structure

The root of the JSON object is the `HydratedJSON` model, which is composed of the following top-level keys:

| Key | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `case_information` | Object | Yes | Metadata about the case and document type. |
| `parties` | Object | Yes | Contains information about the plaintiff and all defendants. |
| `jurisdiction_and_venue` | Object | Yes | Details on the legal basis for the court's authority. |
| `preliminary_statement` | String | Yes | A brief, introductory summary of the case. |
| `factual_background` | Object | Yes | A summary of the events that led to the lawsuit. |
| `causes_of_action` | Array of Objects | Yes | A list of the specific legal claims being made. |
| `prayer_for_relief` | Object | Yes | A summary of the damages and remedies sought. |
| `jury_demand` | Boolean | Yes | A true/false value indicating if a jury trial is requested. |
| `filing_details` | Object | Yes | Dates related to the filing of the document. |
| `metadata` | Object | Yes | Internal metadata for tracking and versioning. |

---

## 3. Detailed Field Explanations

### 3.1. `case_information`

Contains high-level details about the legal case.

| Field | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `court_name` | String | Yes | The full name of the court (e.g., "UNITED STATES DISTRICT COURT"). |
| `court_district` | String | Yes | The district of the court (e.g., "Eastern District of New York"). |
| `case_number` | String | Yes | The official case number assigned by the court. |
| `document_title` | String | Yes | The title of the document being generated (e.g., "COMPLAINT"). |
| `document_type` | String | Yes | The type of case, used for template selection (e.g., "FCRA"). Defaults to "FCRA". |

### 3.2. `parties`

Contains details about all parties involved in the case.

| Field | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `plaintiff` | Object | Yes | An object containing the plaintiff's information. |
| `defendants` | Array of Objects | Yes | A list of objects, where each object represents a defendant. |

#### **Plaintiff Object**

| Field | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | String | Yes | The full name of the plaintiff. |
| `address` | Object | Yes | An object containing the plaintiff's address. |
| `residency` | String | Yes | The plaintiff's area of residence (e.g., "Borough of Manhattan"). |
| `consumer_status` | String | Yes | The plaintiff's legal status under the relevant laws. |

#### **Defendant Object**

| Field | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | String | Yes | The full legal name of the defendant. |
| `short_name` | String | **Yes** | A shortened, convenient name for the defendant (e.g., "Equifax"). **This is a required field.** |
| `type` | String | Yes | The defendant's role (e.g., "Consumer Reporting Agency", "Furnisher of Information"). |
| `state_of_incorporation` | String | Yes | The state where the defendant company is incorporated. |
| `business_status` | String | Yes | The defendant's status regarding doing business in the relevant state. |

### 3.3. `causes_of_action`

This is an array of `CauseOfAction` objects. Each object represents a specific legal claim.

#### **CauseOfAction Object**

| Field | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `count_number` | Integer | **Yes** | The sequential number of the cause of action (e.g., 1, 2, 3). **This is a required field.** |
| `title` | String | Yes | The title of the legal claim (e.g., "FIRST CAUSE OF ACTION: Violation of the FCRA"). |
| `against_defendants`| Array of Strings | Yes | A list of the `short_name`s of the defendants this claim is against. |
| `allegations` | Array of Objects | Yes | A list of the specific statutory violations alleged under this cause of action. |

#### **Allegation Object**

| Field | Data Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `citation` | String | Yes | The legal citation for the violation (e.g., "15 U.S.C. § 1681i"). |
| `description` | String | Yes | A plain-language description of the alleged violation. |
| `against_defendants`| Array of Strings | No | An optional list of the `short_name`s of the defendants this specific allegation is against. |

---

## 4. Example Snippet

This snippet shows the correct structure for the `parties` and `causes_of_action` sections, highlighting the required `short_name` and `count_number` fields.

```json
{
  "parties": {
    "plaintiff": { ... },
    "defendants": [
      {
        "name": "EQUIFAX INFORMATION SERVICES LLC",
        "short_name": "Equifax",
        "type": "Consumer Reporting Agency",
        "state_of_incorporation": "Georgia",
        "business_status": "Authorized to do business in New York"
      }
    ]
  },
  "causes_of_action": [
    {
      "count_number": 1,
      "title": "FIRST CAUSE OF ACTION: Violation of the FCRA",
      "against_defendants": ["Equifax"],
      "allegations": [
        {
          "citation": "15 U.S.C. § 1681i",
          "description": "Failure to conduct reasonable reinvestigations of the plaintiff's disputes."
        }
      ]
    }
  ]
}
```
