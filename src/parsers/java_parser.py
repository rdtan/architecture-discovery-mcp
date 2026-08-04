from pathlib import Path
from dataclasses import dataclass, field

import javalang


@dataclass
class JavaMethod:
    name: str
    return_type: str = ""
    parameters: list[dict] = field(default_factory=list)
    annotations: list[dict] = field(default_factory=list)
    body: object | None = None


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
    extends_class: str = ""
    documentation: str = ""


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
        m.body = _parse_method_body(method)
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
                    ann_list = []
                    for a in f.annotations:
                        detail = {"name": a.name, "params": {}}
                        if a.element:
                            if isinstance(a.element, list):
                                detail["params"] = {
                                    e.name: _annotation_value(e.value)
                                    for e in a.element
                                }
                            else:
                                detail["params"] = {"value": _annotation_value(a.element)}
                        ann_list.append(detail)
                    field_info["annotations"] = ann_list
                fields.append(field_info)

    extends_class = ""
    if hasattr(node, "extends") and node.extends:
        if hasattr(node.extends, "name"):
            extends_class = node.extends.name

    documentation = node.documentation or "" if hasattr(node, "documentation") else ""

    return JavaClass(
        class_name=node.name,
        package_name=package_name,
        annotations=annotations,
        annotation_details=annotation_details,
        methods=methods,
        fields=fields,
        is_interface=is_interface,
        imports=imports,
        extends_class=extends_class,
        documentation=documentation,
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


def _walk_tree(node):
    """Recursively yield all nodes in a javalang AST subtree."""
    if isinstance(node, (list, tuple)):
        for item in node:
            yield from _walk_tree(item)
    elif hasattr(node, 'children'):
        yield node
        for child in node.children:
            if child is not None:
                yield from _walk_tree(child)


def _parse_method_body(method_node) -> dict | None:
    """Parse a method body, extracting invocations and local variable declarations.

    Returns None if the method has no body (abstract/interface methods).
    """
    if method_node.body is None:
        return None

    invocations = []
    local_variables = []

    for node in _walk_tree(method_node.body):
        if isinstance(node, javalang.tree.MethodInvocation):
            qualifier = node.qualifier if node.qualifier else ""
            method_name = node.member
            arguments = [str(arg) for arg in node.arguments] if node.arguments else []
            line_number = node.position.line if node.position else 0
            invocations.append({
                "qualifier": qualifier,
                "method_name": method_name,
                "arguments": arguments,
                "line_number": line_number,
            })
        elif isinstance(node, javalang.tree.LocalVariableDeclaration):
            type_name = node.type.name if node.type else ""
            line_number = node.position.line if node.position else 0
            if node.declarators:
                for decl in node.declarators:
                    local_variables.append({
                        "name": decl.name,
                        "type_name": type_name,
                        "line_number": line_number,
                    })

    return {
        "invocations": invocations,
        "local_variables": local_variables,
    }
