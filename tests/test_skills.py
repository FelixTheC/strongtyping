from pathlib import Path

import yaml


def get_skills_dir():
    # Adjusted to look for src/strongtyping/skills
    root = Path(__file__).parent.parent
    skills_dir = root / "src" / "strongtyping" / "skills"
    return skills_dir


def test_skills_structure():
    skills_dir = get_skills_dir()
    assert skills_dir.exists(), f"Skills directory not found at {skills_dir}"

    skill_folders = [f for f in skills_dir.iterdir() if f.is_dir()]
    assert len(skill_folders) > 0, "No skill folders found in skills directory"

    for skill_folder in skill_folders:
        skill_file = skill_folder / "SKILL.md"
        assert skill_file.exists(), f"SKILL.md missing in {skill_folder.name}"


def test_skill_content_validation():
    skills_dir = get_skills_dir()
    skill_folders = [f for f in skills_dir.iterdir() if f.is_dir()]

    for skill_folder in skill_folders:
        skill_file = skill_folder / "SKILL.md"
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for YAML frontmatter
        assert content.startswith(
            "---"
        ), f"SKILL.md in {skill_folder.name} missing YAML frontmatter start"

        parts = content.split("---", 2)
        assert (
            len(parts) >= 3
        ), f"SKILL.md in {skill_folder.name} has invalid YAML frontmatter structure"

        yaml_content = parts[1]
        data = yaml.safe_load(yaml_content)

        # Validate required fields
        assert (
            "name" in data
        ), f"Missing 'name' in YAML frontmatter of {skill_folder.name}"
        assert (
            "description" in data
        ), f"Missing 'description' in YAML frontmatter of {skill_folder.name}"

        # Conventions
        assert (
            data["name"] == skill_folder.name
        ), f"Skill name '{data['name']}' does not match directory name '{skill_folder.name}'"
        assert (
            len(data["description"]) > 10
        ), f"Description for {skill_folder.name} is too short"


def test_skill_markdown_content():
    skills_dir = get_skills_dir()
    skill_folders = [f for f in skills_dir.iterdir() if f.is_dir()]

    for skill_folder in skill_folders:
        skill_file = skill_folder / "SKILL.md"
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.split("---", 2)
        markdown_body = parts[2].strip()

        assert (
            len(markdown_body) > 0
        ), f"SKILL.md in {skill_folder.name} has no markdown content"
        assert (
            "# " in markdown_body
        ), f"SKILL.md in {skill_folder.name} should have at least one H1 header"


def test_pyproject_includes_skills():
    import tomllib

    root = Path(__file__).parent.parent
    pyproject_path = root / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    package_data = data.get("tool", {}).get("setuptools", {}).get("package-data", {})
    strongtyping_data = package_data.get("strongtyping", [])

    assert (
        "skills/**/*" in strongtyping_data
    ), "skills/**/* should be included in [tool.setuptools.package-data].strongtyping"
