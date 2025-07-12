# !/bin/bash

# 后端
cd /workspace/backend
uv run autopep8 app
uv run pylint app

# 前端
cd /workspace/frontend
bun lint