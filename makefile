install:
	uv sync --all-extras --no-install-project
	uv export -o requirements.txt

start:
	func start
