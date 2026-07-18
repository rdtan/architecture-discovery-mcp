from pathlib import Path
from dataclasses import dataclass, field

import javalang


@dataclass
class JavaMethod:
    name: str
    return_type: str = ""
    parameters: list[dict] = field(default_factory=list)
    annotations: list[dict] = field(default_factory=list)


@dataclass
class JavaClass:
    class_name: str
    package_name: str
    annotations: list[str] = field(default_factory=list)
    annotation_details: list[dict] = field(default_factory=list)
    methods: list[JavaMethod] = field(default_factory=list)
    fields: list[dict] = field(default_factory=list)
    is_interface: bool = False
    imports: list[str] = field(default_factory=list)


def parse_java_file(file_path: Path) -> JavaClass | None:
    """Parse a Java source file into a JavaClass dataclass.

    Returns None if the file cannot be parsed (graceful failure).
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = javalang.parse.parse(source)
    except (javalang.parser.JavaSyntaxError, Exception):
        return None

    package_name = tree.package.name if tree.package else ""
    imports = [imp.path for imp in tree.imports] if tree.imports else []

    # Try class declarations first, then interfaces
    for _, node in tree.filter(javalang.tree.ClassDeclaration):
        return _build_java_class(node, package_name, imports, is_interface=False)

    for _, node in tree.filter(javalang.tree.InterfaceDeclaration):
        return _build_java_class(node, package_name, imports, is_interface=True)

    return None


def _build_java_class(
    node, package_name: str, imports: list[str], is_interface: bool
) -> JavaClass:
    """Build a JavaClass from a javalang AST node."""
    annotations = []
    annotation_details = []
    if node.annotations:
        for ann in node.annotations:
            annotations.append(ann.name)
            detail = {"name": ann.name}
            if ann.element:
                if isinstance(ann.element, list):
                    detail["params"] = {
                        e.name: _annotation_value(e.value) for e in ann.element
                    }
                else:
                    detail["value"] = _annotation_value(ann.element)
            annotation_details.append(detail)

    methods = []
    method_declarations = (
        node.methods if hasattr(node, "methods") and node.methods else []
    )
    for method in method_declarations:
        m = JavaMethod(name=method.name)
        if method.return_type:
            m.return_type = (
                method.return_type.name
                if hasattr(method.return_type, "name")
                else str(method.return_type)
            )
        if method.parameters:
            for param in method.parameters:
                p = {
                    "name": param.name,
                    "type": param.type.name if param.type else "",
                }
                m.parameters.append(p)
        if method.annotations:
            for ann in method.annotations:
                detail = {"name": ann.name}
                if ann.element:
                    if isinstance(ann.element, list):
                        detail["params"] = {
                            e.name: _annotation_value(e.value)
                            for e in ann.element
                        }
                    else:
                        detail["value"] = _annotation_value(ann.element)
                m.annotations.append(detail)
        methods.append(m)

    fields = []
    if hasattr(node, "fields") and node.fields:
        for f in node.fields:
            for decl in f.declarators:
                field_info = {
                    "name": decl.name,
                    "type": f.type.name if f.type else "",
                }
                if f.annotations:
                    field_info["annotations"] = [a.name for a in f.annotations]
                fields.append(field_info)

    return JavaClass(
        class_name=node.name,
        package_name=package_name,
        annotations=annotations,
        annotation_details=annotation_details,
        methods=methods,
        fields=fields,
        is_interface=is_interface,
        imports=imports,
    )


def _annotation_value(value) -> str:
    """Extract a string representation from a javalang annotation value."""
    if isinstance(value, javalang.tree.Literal):
        return value.value.strip('"')
    if isinstance(value, javalang.tree.MemberReference):
        return (
            f"{value.qualifier}.{value.member}" if value.qualifier else value.member
        )
    return str(value)
