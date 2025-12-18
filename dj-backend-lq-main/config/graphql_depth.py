"""
Lightweight GraphQL depth limiter to protect against overly deep queries.
"""

from graphql import GraphQLError
from graphql.language.ast import FragmentSpreadNode, InlineFragmentNode
from graphql.validation.rules import ValidationRule


def _selection_children(selection):
    if not getattr(selection, "selection_set", None):
        return []
    return selection.selection_set.selections


def depth_limit_validator(max_depth: int):
    """
    Return a validation rule class enforcing maximum query depth.
    Introspection queries are excluded from depth validation.
    """

    class DepthLimitRule(ValidationRule):
        def enter_operation_definition(self, node, *_):
            # Skip depth validation for introspection queries
            if self._is_introspection_query(node):
                return
            self._check_depth(node, 0, {})

        def _is_introspection_query(self, node):
            """Check if this is an introspection query by looking at field names."""
            for selection in _selection_children(node):
                field_name = getattr(selection, "name", None)
                if field_name:
                    name_value = getattr(field_name, "value", "")
                    # Introspection queries start with __
                    if name_value.startswith("__"):
                        return True
            return False

        def _check_depth(self, node, depth, fragments):
            if depth > max_depth:
                raise GraphQLError(
                    f"Query is too deep: {depth} > {max_depth}",
                    nodes=[node],
                )

            for selection in _selection_children(node):
                if isinstance(selection, FragmentSpreadNode):
                    name = selection.name.value
                    fragment = self.context.get_fragment(name)
                    if fragment and name not in fragments:
                        fragments[name] = True
                        self._check_depth(fragment, depth + 1, fragments)
                elif isinstance(selection, InlineFragmentNode):
                    self._check_depth(selection, depth + 1, fragments)
                else:
                    self._check_depth(selection, depth + 1, fragments)

    return DepthLimitRule


__all__ = ["depth_limit_validator"]
