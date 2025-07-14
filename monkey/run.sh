#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
./satori-monkey "$@"