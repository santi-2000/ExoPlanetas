#!/bin/bash
cd /Users/santiagoestrda/Downloads/ExoPlanetas
uvicorn backend.main:app --host 127.0.0.1 --port 8000
