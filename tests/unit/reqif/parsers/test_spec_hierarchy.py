from xml.etree import ElementTree

from reqif.parsers.spec_hierarchy_parser import (
    ReqIFSpecHierarchyParser,
)


def test_01_nominal_case() -> None:
    specification_string = """
<SPEC-HIERARCHY IDENTIFIER="LEVEL_1" LAST-CHANGE="2015-12-14T02:04:51.856+01:00">
  <OBJECT>
    <SPEC-OBJECT-REF>TEST_OBJECT_REF_1</SPEC-OBJECT-REF>
  </OBJECT>
  <CHILDREN>
    <SPEC-HIERARCHY IDENTIFIER="LEVEL_1_1" LAST-CHANGE="2015-12-14T02:04:51.857+01:00">
      <OBJECT>
        <SPEC-OBJECT-REF>TEST_OBJECT_REF_1_1</SPEC-OBJECT-REF>
      </OBJECT>
      <CHILDREN>
        <SPEC-HIERARCHY IDENTIFIER="LEVEL_1_1_1" LAST-CHANGE="2015-12-14T02:04:52.271+01:00">
          <OBJECT>
            <SPEC-OBJECT-REF>TEST_OBJECT_REF_1_1_1</SPEC-OBJECT-REF>
          </OBJECT>
        </SPEC-HIERARCHY>
      </CHILDREN>
    </SPEC-HIERARCHY>
  </CHILDREN>
</SPEC-HIERARCHY>
    """  # noqa: E501

    specification_xml = ElementTree.fromstring(specification_string)
    specification_1 = ReqIFSpecHierarchyParser.parse(specification_xml)
    assert specification_1.identifier == "LEVEL_1"
    assert specification_1.spec_object == "TEST_OBJECT_REF_1"
    assert specification_1.level == 1
    assert len(specification_1.children) == 1

    specification_1_1 = specification_1.children[0]
    assert specification_1_1.identifier == "LEVEL_1_1"
    assert len(specification_1_1.children) == 1
    assert specification_1_1.level == 2

    specification_1_1_1 = specification_1_1.children[0]
    assert specification_1_1_1.identifier == "LEVEL_1_1_1"
    assert specification_1_1_1.children is None
    assert specification_1_1_1.level == 3


def test_02_desc() -> None:
    specification_string = """\
<SPEC-HIERARCHY DESC="Some &amp; description" IDENTIFIER="LEVEL_1" LAST-CHANGE="2015-12-14T02:04:51.856+01:00">
  <OBJECT>
    <SPEC-OBJECT-REF>TEST_OBJECT_REF_1</SPEC-OBJECT-REF>
  </OBJECT>
</SPEC-HIERARCHY>
"""  # noqa: E501

    specification_xml = ElementTree.fromstring(specification_string)
    spec_hierarchy = ReqIFSpecHierarchyParser.parse(specification_xml)
    assert spec_hierarchy.description == "Some & description"

    unparsed = ReqIFSpecHierarchyParser.unparse(spec_hierarchy)
    assert unparsed.splitlines()[0].lstrip() == (
        '<SPEC-HIERARCHY DESC="Some &amp; description" IDENTIFIER="LEVEL_1" '
        'LAST-CHANGE="2015-12-14T02:04:51.856+01:00">'
    )


def test_03_no_desc_is_not_emitted() -> None:
    specification_string = """\
<SPEC-HIERARCHY IDENTIFIER="LEVEL_1">
  <OBJECT>
    <SPEC-OBJECT-REF>TEST_OBJECT_REF_1</SPEC-OBJECT-REF>
  </OBJECT>
</SPEC-HIERARCHY>
"""

    specification_xml = ElementTree.fromstring(specification_string)
    spec_hierarchy = ReqIFSpecHierarchyParser.parse(specification_xml)
    assert spec_hierarchy.description is None
    assert "DESC" not in ReqIFSpecHierarchyParser.unparse(spec_hierarchy)
