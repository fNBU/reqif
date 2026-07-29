from xml.etree import ElementTree

from reqif.models.reqif_data_type import ReqIFDataTypeDefinitionString
from reqif.models.reqif_spec_relation_type import ReqIFSpecRelationType
from reqif.parsers.alternative_id_parser import AlternativeIDParser
from reqif.parsers.data_type_parser import DataTypeParser
from reqif.parsers.spec_types.spec_relation_type_parser import (
    SpecRelationTypeParser,
)


def test_01_parse_returns_the_inner_identifier() -> None:
    xml = ElementTree.fromstring(
        """
<SPEC-OBJECT IDENTIFIER="SO1">
  <ALTERNATIVE-ID>
    <ALTERNATIVE-ID IDENTIFIER="ALT_SO1"/>
  </ALTERNATIVE-ID>
</SPEC-OBJECT>
"""
    )
    assert AlternativeIDParser.parse(xml) == "ALT_SO1"


def test_02_absent_and_empty_wrapper_both_parse_to_none() -> None:
    without = ElementTree.fromstring('<SPEC-OBJECT IDENTIFIER="SO1"/>')
    assert AlternativeIDParser.parse(without) is None

    # The schema permits an empty wrapper. It holds no identifier, so there is
    # nothing to model and the element is not preserved.
    empty = ElementTree.fromstring(
        '<SPEC-OBJECT IDENTIFIER="SO1"><ALTERNATIVE-ID/></SPEC-OBJECT>'
    )
    assert AlternativeIDParser.parse(empty) is None


def test_03_unparse_round_trips_the_nested_shape() -> None:
    assert AlternativeIDParser.unparse(None, "  ") == ""
    assert AlternativeIDParser.unparse("ALT_SO1", "  ") == (
        "  <ALTERNATIVE-ID>\n"
        '    <ALTERNATIVE-ID IDENTIFIER="ALT_SO1"/>\n'
        "  </ALTERNATIVE-ID>\n"
    )


def test_04_self_closed_data_type_switches_to_the_open_form() -> None:
    """A self-closed element cannot host a child, so an alternative_id has to
    force the open form or it would be dropped on write."""
    data_type = ReqIFDataTypeDefinitionString(
        identifier="D1", is_self_closed=True, alternative_id="ALT_D1"
    )
    output = DataTypeParser.unparse(data_type)
    assert "ALT_D1" in output
    assert "<DATATYPE-DEFINITION-STRING/>" not in output
    assert "</DATATYPE-DEFINITION-STRING>" in output

    # Without one, the self-closed form is still preserved.
    plain = ReqIFDataTypeDefinitionString(identifier="D1", is_self_closed=True)
    assert "<DATATYPE-DEFINITION-STRING" in DataTypeParser.unparse(plain)
    assert "/>" in DataTypeParser.unparse(plain)


def test_05_self_closed_spec_relation_type_switches_to_the_open_form() -> None:
    spec_relation_type = ReqIFSpecRelationType(
        identifier="T1", is_self_closed=True, alternative_id="ALT_T1"
    )
    output = SpecRelationTypeParser.unparse(spec_relation_type)
    assert "ALT_T1" in output
    assert "</SPEC-RELATION-TYPE>" in output


def test_06_alternative_id_does_not_swap_object_and_children() -> None:
    """ALTERNATIVE-ID is an extra SPEC-HIERARCHY child, and the OBJECT/CHILDREN
    order flag used to compare the whole child list, so preserving it would
    otherwise reverse those two on write."""
    from reqif.parsers.spec_hierarchy_parser import ReqIFSpecHierarchyParser

    spec_hierarchy = ReqIFSpecHierarchyParser.parse(
        ElementTree.fromstring(
            """
<SPEC-HIERARCHY IDENTIFIER="L1">
  <ALTERNATIVE-ID><ALTERNATIVE-ID IDENTIFIER="ALT_L1"/></ALTERNATIVE-ID>
  <OBJECT><SPEC-OBJECT-REF>A</SPEC-OBJECT-REF></OBJECT>
  <CHILDREN>
    <SPEC-HIERARCHY IDENTIFIER="L1_1">
      <OBJECT><SPEC-OBJECT-REF>B</SPEC-OBJECT-REF></OBJECT>
    </SPEC-HIERARCHY>
  </CHILDREN>
</SPEC-HIERARCHY>
"""
        )
    )
    assert spec_hierarchy.alternative_id == "ALT_L1"
    assert spec_hierarchy.ref_then_children_order is True

    unparsed = ReqIFSpecHierarchyParser.unparse(spec_hierarchy)
    assert unparsed.index("<OBJECT>") < unparsed.index("<CHILDREN>")
