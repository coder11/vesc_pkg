"""Bundle a graph of local QML components into one QML document.

Local dependencies use an intentionally narrow convention::

    import "components" as Components

    Item {
        component GaugeRef: Components.Gauge {}
        GaugeRef { }
    }

The empty inline component declaration is replaced with the root object from
``components/Gauge.qml``. Imports from every visited document are promoted to
the generated document, while local directory imports are removed.
"""

from __future__ import annotations

import argparse
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


LOCAL_IMPORT_RE = re.compile(
    r'^\s*import\s+"(?P<path>[^"]+)"\s+as\s+(?P<alias>[A-Z]\w*)\s*$'
)
MODULE_IMPORT_RE = re.compile(
    r"^import\s+(?P<module>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
    r"(?:\s+(?P<version>\d+(?:\.\d+)*))?"
    r"(?:\s+as\s+(?P<alias>[A-Z]\w*))?\s*$"
)
ROOT_RE = re.compile(r"\b(?P<type>[A-Z]\w*(?:\.[A-Z]\w*)*)\s*\{")


class BundleError(RuntimeError):
    """Raised when the source graph does not follow the bundling convention."""


@dataclass(frozen=True)
class LocalImport:
    path: str
    alias: str


@dataclass(frozen=True)
class ModuleImport:
    module: str
    version: tuple[int, ...] | None
    alias: str | None

    @classmethod
    def parse(cls, line: str) -> "ModuleImport":
        match = MODULE_IMPORT_RE.fullmatch(line)
        if match is None:
            raise BundleError(f"unsupported QML import: {line}")
        version_text = match.group("version")
        return cls(
            module=match.group("module"),
            version=(
                tuple(int(part) for part in version_text.split("."))
                if version_text
                else None
            ),
            alias=match.group("alias"),
        )

    @property
    def key(self) -> tuple[str, str | None]:
        return self.module, self.alias

    def render(self) -> str:
        result = f"import {self.module}"
        if self.version is not None:
            result += " " + ".".join(str(part) for part in self.version)
        if self.alias is not None:
            result += f" as {self.alias}"
        return result


@dataclass(frozen=True)
class RootObject:
    type_name: str
    body: str
    open_brace: int
    close_brace: int
    leading_text: str


@dataclass(frozen=True)
class InlineComponent:
    name: str
    root: RootObject
    source_path: Path

    def render(self, indent: str = "    ") -> str:
        leading_text = self.root.leading_text.strip()
        rendered_leading_text = "\n".join(
            indent + line if line.strip() else line
            for line in leading_text.splitlines()
        )
        nested_body = self.root.body.strip("\n")
        nested_body = "\n".join(
            indent + line if line.strip() else line
            for line in nested_body.splitlines()
        )
        component = (
            f"{indent}component {self.name}: {self.root.type_name} {{\n"
            f"{nested_body}\n{indent}}}"
        )
        return (
            f"{rendered_leading_text}\n{component}"
            if rendered_leading_text
            else component
        )


@dataclass
class BundledDocument:
    source_without_imports: str
    imports: dict[tuple[str, str | None], ModuleImport]
    components: dict[str, InlineComponent]


def _merge_import(
    imports: dict[tuple[str, str | None], ModuleImport],
    candidate: ModuleImport,
) -> None:
    current = imports.get(candidate.key)
    if current is None:
        imports[candidate.key] = candidate
        return

    if current.version is None:
        if candidate.version is not None:
            imports[candidate.key] = candidate
        return

    if candidate.version is not None and candidate.version > current.version:
        imports[candidate.key] = candidate


def _merge_imports(
    destination: dict[tuple[str, str | None], ModuleImport],
    source: Iterable[ModuleImport],
) -> None:
    for module_import in source:
        _merge_import(destination, module_import)


def _split_imports(
    source: str, path: Path
) -> tuple[str, list[LocalImport], dict[tuple[str, str | None], ModuleImport]]:
    body_lines: list[str] = []
    local_imports: list[LocalImport] = []
    module_imports: dict[tuple[str, str | None], ModuleImport] = {}

    for line_number, line in enumerate(source.splitlines(keepends=True), start=1):
        stripped = line.strip()
        if not stripped.startswith("import "):
            body_lines.append(line)
            continue

        local_match = LOCAL_IMPORT_RE.fullmatch(stripped)
        if local_match is not None:
            imported_path = local_match.group("path")
            if imported_path.endswith(".js"):
                raise BundleError(
                    f"{path}:{line_number}: JavaScript file imports cannot be bundled"
                )
            local_imports.append(
                LocalImport(imported_path, local_match.group("alias"))
            )
            continue

        try:
            _merge_import(module_imports, ModuleImport.parse(stripped))
        except BundleError as error:
            raise BundleError(f"{path}:{line_number}: {error}") from error

    return "".join(body_lines), local_imports, module_imports


def _mask_comments_and_strings(source: str) -> str:
    """Return same-length text with comments and strings replaced by spaces."""

    result = list(source)
    index = 0
    state = "code"
    quote = ""

    while index < len(source):
        current = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""

        if state == "code":
            if current == "/" and following == "/":
                result[index] = result[index + 1] = " "
                index += 2
                state = "line_comment"
                continue
            if current == "/" and following == "*":
                result[index] = result[index + 1] = " "
                index += 2
                state = "block_comment"
                continue
            if current in ('"', "'"):
                quote = current
                result[index] = " "
                index += 1
                state = "string"
                continue
            index += 1
            continue

        if state == "line_comment":
            if current == "\n":
                state = "code"
            else:
                result[index] = " "
            index += 1
            continue

        if state == "block_comment":
            result[index] = " "
            if current == "*" and following == "/":
                result[index + 1] = " "
                index += 2
                state = "code"
            else:
                index += 1
            continue

        result[index] = " "
        if current == "\\" and following:
            result[index + 1] = " "
            index += 2
        elif current == quote:
            index += 1
            state = "code"
        else:
            index += 1

    if state in {"block_comment", "string"}:
        raise BundleError(f"unterminated {state.replace('_', ' ')}")
    return "".join(result)


def _extract_root(source: str, path: Path) -> RootObject:
    masked = _mask_comments_and_strings(source)
    match = ROOT_RE.search(masked)
    if match is None:
        raise BundleError(f"{path}: could not find a QML root object")

    open_brace = masked.find("{", match.start())
    depth = 1
    index = open_brace + 1
    while index < len(masked) and depth:
        if masked[index] == "{":
            depth += 1
        elif masked[index] == "}":
            depth -= 1
        index += 1

    if depth:
        raise BundleError(f"{path}: root object has an unmatched opening brace")

    trailing = masked[index:]
    if trailing.strip():
        raise BundleError(f"{path}: expected exactly one root QML object")

    return RootObject(
        type_name=match.group("type"),
        body=source[open_brace + 1 : index - 1],
        open_brace=open_brace,
        close_brace=index - 1,
        leading_text=source[: match.start()],
    )


def _merge_component(
    components: dict[str, InlineComponent], candidate: InlineComponent
) -> None:
    current = components.get(candidate.name)
    if current is None:
        components[candidate.name] = candidate
        return
    if (
        current.root.type_name == candidate.root.type_name
        and current.root.body == candidate.root.body
    ):
        return
    raise BundleError(
        f"inline component name {candidate.name} is used by both "
        f"{current.source_path} and {candidate.source_path}; reference names "
        "must be unique across the bundled graph"
    )


class QmlBundler:
    def __init__(self) -> None:
        self._cache: dict[Path, BundledDocument] = {}

    def bundle(self, entrypoint: Path) -> str:
        entrypoint = entrypoint.resolve()
        document = self._bundle_document(entrypoint, ())
        source = document.source_without_imports
        if document.components:
            root = _extract_root(source, entrypoint)
            rendered_components = "\n\n".join(
                component.render() for component in document.components.values()
            )
            source = (
                source[: root.open_brace + 1]
                + "\n"
                + rendered_components
                + "\n"
                + source[root.open_brace + 1 :]
            )
        imports = "\n".join(
            module_import.render() for module_import in document.imports.values()
        )
        body = source.lstrip("\n")
        return f"{imports}\n\n{body}" if imports else body

    def _bundle_document(
        self, path: Path, stack: tuple[Path, ...]
    ) -> BundledDocument:
        path = path.resolve()
        cached = self._cache.get(path)
        if cached is not None:
            return cached
        if path in stack:
            cycle = " -> ".join(item.name for item in (*stack, path))
            raise BundleError(f"cyclic QML component dependency: {cycle}")
        if not path.is_file():
            raise BundleError(f"QML component does not exist: {path}")

        source = path.read_text(encoding="utf-8")
        body, local_imports, imports = _split_imports(source, path)
        components: dict[str, InlineComponent] = {}

        for local_import in local_imports:
            pattern = re.compile(
                rf"(?m)^(?P<indent>[ \t]*)component\s+"
                rf"(?P<reference>[A-Z]\w*)\s*:\s*"
                rf"{re.escape(local_import.alias)}\."
                rf"(?P<component>[A-Z]\w*)\s*\{{\s*\}}"
            )
            matched_components: set[str] = set()

            def replace_reference(match: re.Match[str]) -> str:
                component_name = match.group("component")
                matched_components.add(component_name)
                dependency_path = (
                    path.parent / local_import.path / f"{component_name}.qml"
                )
                dependency = self._bundle_document(
                    dependency_path, (*stack, path)
                )
                _merge_imports(imports, dependency.imports.values())
                for component in dependency.components.values():
                    _merge_component(components, component)
                root = _extract_root(dependency.source_without_imports, dependency_path)
                _merge_component(
                    components,
                    InlineComponent(
                        name=match.group("reference"),
                        root=root,
                        source_path=dependency_path.resolve(),
                    ),
                )
                return ""

            body = pattern.sub(replace_reference, body)
            if not matched_components:
                raise BundleError(
                    f'{path}: import "{local_import.path}" as '
                    f"{local_import.alias} has no empty inline component references"
                )

            remaining_reference = re.search(
                rf"\b{re.escape(local_import.alias)}\.[A-Z]\w*",
                _mask_comments_and_strings(body),
            )
            if remaining_reference is not None:
                line = body.count("\n", 0, remaining_reference.start()) + 1
                raise BundleError(
                    f"{path}:{line}: {local_import.alias} dependencies must be "
                    "declared as empty inline component references"
                )

        document = BundledDocument(body, imports, components)
        self._cache[path] = document
        return document


def bundle_qml(entrypoint: Path, definitions: dict[str, str] | None = None) -> str:
    result = QmlBundler().bundle(entrypoint)
    for name, value in (definitions or {}).items():
        placeholder = "{{" + name + "}}"
        if placeholder not in result:
            raise BundleError(f"placeholder {placeholder} was not found")
        result = result.replace(placeholder, value)
    return result


def write_if_changed(path: Path, content: str) -> None:
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def _parse_definitions(values: list[str]) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for value in values:
        name, separator, replacement = value.partition("=")
        if not separator or not name:
            raise BundleError(f"invalid definition {value!r}; expected NAME=VALUE")
        definitions[name] = replacement
    return definitions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrypoint", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--define",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="replace a {{NAME}} placeholder after bundling",
    )
    arguments = parser.parse_args()

    try:
        content = bundle_qml(
            arguments.entrypoint,
            definitions=_parse_definitions(arguments.define),
        )
        write_if_changed(arguments.output, content)
    except BundleError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
