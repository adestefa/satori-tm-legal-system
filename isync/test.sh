curl -X POST http://127.0.0.1:8000/api/settings \
    -H "Content-Type: application/json" \
    -d '{
      "firm": {
        "name": "Mallon Consumer Law Group, PLLC",
        "address": "238 Merritt Drive\nOradell, NJ. 07649",
        "phone": "(917) 734-6815",
        "email": "kmallon@consmerprotectionfirm.com"
      },
      "document": {
        "default_court": "UNITED STATES DISTRICT COURT",
        "default_district": "EASTERN DISTRICT OF NEW YORK"
      },
      "icloud": {
        "account": "anthony.destefano@gmail.com",
        "password": "zpcc-qsrx-saut-khph",
        "folder": "/CASES"
      },
      "system": {
        "auto_save": true,
        "data_retention": 180
      }
    }'