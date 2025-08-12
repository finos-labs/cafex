"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

root = Path(__file__).parent.parent
component_name = "libs"  # Component containing multiple modules
docs_dir = root / "docs"  # Path to your "docs" directory

# Iterate through each module directory within "libs"
for module_dir in (root / component_name).iterdir():
    if module_dir.is_dir() and (module_dir / "src").exists():
        src = module_dir / "src"

        for path in sorted(src.rglob("*.py")):
            # Make paths relative to the individual module's src
            module_path = path.relative_to(src).with_suffix("")
            doc_path = path.relative_to(src).with_suffix(".md")
            full_doc_path = docs_dir / "reference" / doc_path

            parts = tuple(module_path.parts)

            if parts[-1] == "__init__":
                parts = parts[:-1]
                doc_path = Path(*parts, "index.md")
                full_doc_path = docs_dir / "reference" / Path(*parts, "index.md")
            elif parts[-1] == "__main__":
                continue

            nav[parts] = doc_path.as_posix()

            with mkdocs_gen_files.open(full_doc_path, "w") as fd:
                ident = ".".join(parts)
                fd.write(f"::: {ident}")

            mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

with mkdocs_gen_files.open(docs_dir / "reference" / "SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())