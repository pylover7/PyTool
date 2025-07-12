# !/bin/bash

# 后端
cd backend
uv run autopep8 app
uv run pylint app