"""Tests for merge command with stanzas that exist only in default file.

This test specifically covers the case where the default file has more stanzas
than the local file, and the default-only stanzas contain multiline values
that should be preserved during merge.
"""

import tempfile
from pathlib import Path

from bydefault.utils.change_detection import _parse_conf_file
from bydefault.utils.merge_utils import ConfigMerger


def test_merge_preserves_default_only_multiline_stanzas():
    """Test that multiline values in default-only stanzas are preserved during merge."""

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create TA directory structure
        ta_dir = Path(temp_dir) / "test_ta"
        local_dir = ta_dir / "local"
        default_dir = ta_dir / "default"
        local_dir.mkdir(parents=True)
        default_dir.mkdir(parents=True)

        # Create local file with only one stanza (matches user's scenario)
        local_file = local_dir / "some_db_inputs.conf"
        local_content = """[some_fake_db_input2]
batch_upload_size = 1000
connection = SOME_CONNECTION
disabled = 1
fetch_size = 300
host = some_host.org
index = some_index
index_time_mode = current
input_type = event
interval = 00 00 * * *
max_rows = 0
max_single_checkpoint_file_size = 10485760
mode = batch
query = /*Changes on 5-01-18\\
1) Added join to FIELD_NAME for encounter type\\
2) Added logic to exclude test USERS\\
3) Added logic to include LOCATION encounters\\
4) Revert to original time formats\\
*/\\
\\
SELECT DISTINCT\\
p.field_of_somekind,\\
CASE WHEN field is not null then CONVERT(DATE, field)\\
WHEN some SQL (HERE)\\
END as THING,\\
CONVERT(DATE, ASDAS)  ASD,\\
ASDASD,\\
ASDASD ,\\
hASDAS, \\
fsdf as asdfgqw /*Changed to use afsfqwdE*/,\\
upper(sadsd)          asdqwd,\\
asdqwf  LOCATION \\
,qwghfsdfg as asdqwvv\\
,wqefasdf qwexfa\\
,cqwedzsd\\
,cawdqWE,\\
upper(jqwedqwe)  ewfwefS, \\
upper(qweqwfas)  qwdasd ,\\
qweqwe fvasfdg,\\
CONVERT(DATE,waersfgas) dsfqw\\
some change,\\
,wqfsdg as Veswarfwe\\
,ewagasdfg as asgsdf\\
\\
from qweo.feiasd blah
INNER join qweo.feiasd blah           on \\
LEFT JOIN qweo.feiasd blah    ON some thingbefore line break\\
LEFT JOIN qweo.feiasd blah    ON some thingbefore line break\\
left join qweo.feiasd blah    on some thingbefore line break\\
left join qweo.feiasd blah    on some thingbefore line break\\
left JOIN qweo.feiasd blah    ON some thingbefore line break\\
left JOIN qweo.feiasd blah    ON some thingbefore line break\\
left join qweo.feiasd blah    on some thingbefore line break\\
left join qweo.feiasd blah    on some thingbefore line break\\
left join qweo.feiasd blah    on some thingbefore line break\\
left join qweo.feiasd blah    on some thingbefore line break\\
left join qweo.feiasd blah    ON some thingbefore line break\\
LEFT JOIN qweo.feiasd blah    ON some thingbefore line break\\
LEFT JOIN qweo.feiasd blah    ON some thingbefore line break\\
LEFT JOIN qweo.feiasd blah    ON some thingbefore line break\\
LEFT JOIN qweo.feiasd blah     ON     asodkj\\ 
where \\
((CONVERT(DATE, fwefas) >= dateadd(day,datediff(day,15,GETDATE()),0) AND CONVERT(DATE, asdqwd) < dateadd(day,datediff(day,-15,GETDATE()),0))\\
or \\
CONVERT(DATE, sdawwq) >= dateadd(day,datediff(day,15,GETDATE()),0))\\
and asdqwe <> 'Y' /*Aasdqweqwes*/\\
\\
ORDER BY 1
query_timeout = 10000
source = some:source
sourcetype = some:sourcetype:here
"""
        local_file.write_text(local_content)

        # Create default file with multiple stanzas including default-only ones (matches user's scenario)
        default_file = default_dir / "some_db_inputs.conf"
        default_content = """[some_fake_db_input2]
batch_upload_size = 1000
connection = SOME_CONNECTION
disabled = 1
fetch_size = 300
host = some_host.org
index = some_index
index_time_mode = current
input_type = event
interval = 00 00 * * *
max_rows = 0
max_single_checkpoint_file_size = 10485760
mode = batch
query = /*Changes on 5-01-18\\
1) Added join to FIELD_NAME for encounter type\\
2) Added logic to exclude test USERS\\
3) Added logic to include LOCATION encounters\\
4) Revert to original time formats\\
*/\\
\\
SELECT DISTINCT\\
p.field_of_somekind,\\
CASE WHEN field is not null then CONVERT(DATE, field)\\
WHEN some SQL (HERE)\\
END as THING,\\
CONVERT(DATE, ASDAS)  ASD,\\
ASDASD,\\
ASDASD ,\\
hASDAS, \\
fsdf as asdfgqw /*Changed to use afsfqwdE*/,\\
upper(sadsd)          asdqwd,\\
asdqwf  LOCATION \\
,qwghfsdfg as asdqwvv\\
,wqefasdf qwexfa\\
,cqwedzsd\\
,cawdqWE,\\
upper(jqwedqwe)  ewfwefS, \\
upper(qweqwfas)  qwdasd ,\\
qweqwe fvasfdg,\\
CONVERT(DATE,waersfgas) dsfqw\\
some change,\\
,wqfsdg as Veswarfwe\\
,ewagasdfg as asgsdf\\
\\
from qweo.feiasd blah
((CONVERT(DATE, fwefas) >= dateadd(day,datediff(day,15,GETDATE()),0) AND CONVERT(DATE, asdqwd) < dateadd(day,datediff(day,-15,GETDATE()),0))\\
or \\
CONVERT(DATE, sdawwq) >= dateadd(day,datediff(day,15,GETDATE()),0))\\
and asdqwe <> 'Y' /*Aasdqweqwes*/\\
\\
ORDER BY 1
query_timeout = 10000
source = some:source
sourcetype = some:sourcetype:here

[some_fake_db_input]
batch_upload_size = 1000
connection = SOME_CONNECTION
disabled = 1
fetch_size = 300
host = some_host.org
index = some_index
index_time_mode = current
input_type = event
interval = 00 00 * * *
max_rows = 0
max_single_checkpoint_file_size = 10485760
mode = batch
query = /*Changes on 5-01-18\\
1) Added join to FIELD_NAME for encounter type\\
2) Added logic to exclude test USERS\\
3) Added logic to include LOCATION encounters\\
4) Revert to original time formats\\
*/\\
\\
SELECT DISTINCT\\
p.field_of_somekind,\\
CASE WHEN field is not null then CONVERT(DATE, field)\\
WHEN some SQL (HERE)\\
END as THING,\\
CONVERT(DATE, ASDAS)  ASD,\\
ASDASD,\\
ASDASD ,\\
hASDAS, \\
fsdf as asdfgqw /*Changed to use afsfqwdE*/,\\
upper(sadsd)          asdqwd,\\
asdqwf  LOCATION \\
,qwghfsdfg as asdqwvv\\
,wqefasdf qwexfa\\
,cqwedzsd\\
,cawdqWE,\\
upper(jqwedqwe)  ewfwefS, \\
upper(qweqwfas)  qwdasd ,\\
qweqwe fvasfdg,\\
CONVERT(DATE,waersfgas) dsfqw\\
,wqfsdg as Veswarfwe\\
,ewagasdfg as asgsdf\\
\\
from qweo.feiasd blah
((CONVERT(DATE, fwefas) >= dateadd(day,datediff(day,15,GETDATE()),0) AND CONVERT(DATE, asdqwd) < dateadd(day,datediff(day,-15,GETDATE()),0))\\
or \\
CONVERT(DATE, sdawwq) >= dateadd(day,datediff(day,15,GETDATE()),0))\\
and asdqwe <> 'Y' /*Aasdqweqwes*/\\
\\
ORDER BY 1
query_timeout = 10000
source = some:source
sourcetype = some:sourcetype:here

[some_fake_db_input3]
batch_upload_size = 1000
connection = SOME_CONNECTION
disabled = 1
fetch_size = 300
host = some_host.org
index = some_index
index_time_mode = current
input_type = event
interval = 00 00 * * *
max_rows = 0
max_single_checkpoint_file_size = 10485760
mode = batch
query = /*Changes on 5-01-18\\
1) Added join to FIELD_NAME for encounter type\\
2) Added logic to exclude test USERS\\
3) Added logic to include LOCATION encounters\\
4) Revert to original time formats\\
*/\\
\\
SELECT DISTINCT\\
p.field_of_somekind,\\
CASE WHEN field is not null then CONVERT(DATE, field)\\
WHEN some SQL (HERE)\\
END as THING,\\
CONVERT(DATE, ASDAS)  ASD,\\
ASDASD,\\
ASDASD ,\\
hASDAS, \\
fsdf as asdfgqw /*Changed to use afsfqwdE*/,\\
upper(sadsd)          asdqwd,\\
asdqwf  LOCATION \\
,qwghfsdfg as asdqwvv\\
,wqefasdf qwexfa\\
,cqwedzsd\\
,cawdqWE,\\
upper(jqwedqwe)  ewfwefS, \\
upper(qweqwfas)  qwdasd ,\\
qweqwe fvasfdg,\\
CONVERT(DATE,waersfgas) dsfqw\\
,wqfsdg as Veswarfwe\\
,ewagasdfg as asgsdf\\
\\
from qweo.feiasd blah
((CONVERT(DATE, fwefas) >= dateadd(day,datediff(day,15,GETDATE()),0) AND CONVERT(DATE, asdqwd) < dateadd(day,datediff(day,-15,GETDATE()),0))\\
or \\
CONVERT(DATE, sdawwq) >= dateadd(day,datediff(day,15,GETDATE()),0))\\
and asdqwe <> 'Y' /*Aasdqweqwes*/\\
\\
ORDER BY 1
query_timeout = 10000
source = some:source
sourcetype = some:sourcetype:here

[aome_fake_db_input]
batch_upload_size = 1000
connection = SOME_CONNECTION
disabled = 1
fetch_size = 300
host = some_host.org
index = some_index
index_time_mode = current
input_type = event
interval = 00 00 * * *
max_rows = 0
max_single_checkpoint_file_size = 10485760
mode = batch
query = /*Changes on 5-01-18\\
1) Added join to FIELD_NAME for encounter type\\
2) Added logic to exclude test USERS\\
3) Added logic to include LOCATION encounters\\
4) Revert to original time formats\\
*/\\
\\
SELECT DISTINCT\\
p.field_of_somekind,\\
CASE WHEN field is not null then CONVERT(DATE, field)\\
WHEN some SQL (HERE)\\
END as THING,\\
CONVERT(DATE, ASDAS)  ASD,\\
ASDASD,\\
ASDASD ,\\
hASDAS, \\
fsdf as asdfgqw /*Changed to use afsfqwdE*/,\\
upper(sadsd)          asdqwd,\\
asdqwf  LOCATION \\
,qwghfsdfg as asdqwvv\\
,wqefasdf qwexfa\\
,cqwedzsd\\
,cawdqWE,\\
upper(jqwedqwe)  ewfwefS, \\
upper(qweqwfas)  qwdasd ,\\
qweqwe fvasfdg,\\
CONVERT(DATE,waersfgas) dsfqw\\
,wqfsdg as Veswarfwe\\
,ewagasdfg as asgsdf\\
\\
from qweo.feiasd blah
((CONVERT(DATE, fwefas) >= dateadd(day,datediff(day,15,GETDATE()),0) AND CONVERT(DATE, asdqwd) < dateadd(day,datediff(day,-15,GETDATE()),0))\\
or \\
CONVERT(DATE, sdawwq) >= dateadd(day,datediff(day,15,GETDATE()),0))\\
and asdqwe <> 'Y' /*Aasdqweqwes*/\\
\\
ORDER BY 1
query_timeout = 10000
source = some:source
sourcetype = some:sourcetype:here

"""
        default_file.write_text(default_content)

        print(f"\nBEFORE MERGE - Local content:\n{local_file.read_text()}")
        print(f"\nBEFORE MERGE - Default content:\n{default_file.read_text()}")

        # Parse the original default file to verify it has multiline values
        original_default_parsed = _parse_conf_file(default_file)
        print(
            f"\nDefault-only stanzas to test: {set(original_default_parsed.keys()) - {'some_fake_db_input2'}}"
        )

        # Verify original multiline formatting in default-only stanzas
        for stanza_name in [
            "some_fake_db_input",
            "some_fake_db_input3",
            "aome_fake_db_input",
        ]:
            assert stanza_name in original_default_parsed
            query_value = original_default_parsed[stanza_name]["query"]
            # Should contain multiline content parsed properly
            assert "Changes on 5-01-18 1) Added join" in query_value
            assert "SELECT DISTINCT" in query_value

        # Merge the files
        merger = ConfigMerger(ta_dir)
        result = merger.merge()
        merger.write()

        # Verify the merge was successful
        assert result.success

        # Read the merged file
        merged_content = default_file.read_text()
        print(f"\nAFTER MERGE - Content:\n{merged_content}")

        # Parse the merged file
        merged_parsed = _parse_conf_file(default_file)

        # Verify all stanzas are present
        expected_stanzas = {
            "some_fake_db_input2",
            "some_fake_db_input",
            "some_fake_db_input3",
            "aome_fake_db_input",
        }
        assert set(merged_parsed.keys()) == expected_stanzas

        # Key test: Verify that default-only stanzas preserve their multiline formatting
        for stanza_name in [
            "some_fake_db_input",
            "some_fake_db_input3",
            "aome_fake_db_input",
        ]:
            # Check that the stanza exists in merged result
            assert (
                stanza_name in merged_parsed
            ), f"Stanza {stanza_name} missing from merged result"

            # Check that the query setting exists and has multiline content
            assert (
                "query" in merged_parsed[stanza_name]
            ), f"Query setting missing from {stanza_name}"

            # The key test: multiline formatting should be preserved in the file content
            # Look for the backslash continuations in the raw file content
            stanza_section_start = merged_content.find(f"[{stanza_name}]")
            assert (
                stanza_section_start != -1
            ), f"Could not find stanza {stanza_name} in merged content"

            # Find the next stanza or end of file to get this stanza's content
            next_stanza_start = merged_content.find("\n[", stanza_section_start + 1)
            if next_stanza_start == -1:
                stanza_content = merged_content[stanza_section_start:]
            else:
                stanza_content = merged_content[stanza_section_start:next_stanza_start]

            # Verify multiline formatting is preserved (backslashes should be present)
            assert (
                "/*Changes on 5-01-18\\" in stanza_content
            ), f"Missing multiline comment start in {stanza_name}"
            assert (
                "SELECT DISTINCT\\" in stanza_content
            ), f"Missing multiline SELECT in {stanza_name}"
            assert (
                "ORDER BY 1" in stanza_content
            ), f"Missing ORDER BY clause in {stanza_name}"

            # Count the number of backslashes to ensure multiline structure is intact
            backslash_count = stanza_content.count("\\")
            assert (
                backslash_count >= 20
            ), f"Too few backslashes in {stanza_name} - multiline structure may be broken (found {backslash_count})"

        print(
            "\n✅ All default-only stanzas preserved their multiline formatting correctly!"
        )


if __name__ == "__main__":
    test_merge_preserves_default_only_multiline_stanzas()
    print("Test passed!")
