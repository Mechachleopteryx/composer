from .files import (
    make_file,
    contain_file_mutation,
    copy_file,
)
from .parsing import (
    is_section_separator,
    get_section_pattern,
    SECTION_OR_EOF_PATTERN,
    SECTION_SEPARATOR,
    is_eof,
    is_subtask,
)


# This module roughly contains the abstraction level between core planner logic
# and the underlying (filesystem) representation. It roughly deals in "entries"
# and lists of entries, which themselves may be moved between sections in a
# logfile. It should ideally facilitate a separation point where higher-level
# code does not deal in files anymore but rather in entries or sections or
# whatever other high-level abstractions make sense for the planner. This
# separation isn't quite achieved at the moment, and so abstractions do
# currently leak between the layers


def item_list_to_string(items):
    return "".join(items)


def string_to_item_list(string):
    items, _ = get_task_items(make_file(string))
    return items


def filter_items(item_list, filter_fn):
    """ Filter an item list to only those that satisfy a given filter function.
    """
    return [item for item in item_list if filter_fn(item)]


def exclude_items(item_list, filter_fn):
    """ Filter an item list to only those that do NOT satisfy a given
    filter function.
    """
    return [item for item in item_list if not filter_fn(item)]


def partition_items(item_list, filter_fn):
    """ Partition an item list into two lists based on some filter predicate.
    The first list will contain the elements that satisfy the predicate, while
    the second list will contain those that don't.
    """
    filtered = filter_items(item_list, filter_fn)
    excluded = exclude_items(item_list, filter_fn)
    return filtered, excluded


@contain_file_mutation
def read_item(file):
    """ An 'item' is any line that begins at the 0th position of the line.
    This could be a blank line, a task, a normal text string, a section
    header, pretty much anything EXCEPT things that begin with a tab
    character, as these are treated as subsidiary items to be included in
    the parent.

    :param :class:`io.StringIO` file: The file to read from

    :returns str: An item read from the file
    """
    item = ""
    complement = make_file()
    line = file.readline()
    if is_eof(line):
        complement = make_file(file.getvalue())
        return None, complement
    item += line
    line = file.readline()
    while is_subtask(line):
        item += line
        line = file.readline()
    complement.write(line)
    complement.write(file.read())
    return item, complement


def _read_items(file):
    items = []
    item, complement = read_item(file)
    while item:
        items.append(item)
        item, complement = read_item(complement)
    return items


@contain_file_mutation
def get_task_items(file, of_type=None):
    """ Parse a given file into task items, based on the supplied criteria.
    A task item generally corresponds to a line in the input file, along with
    any subtasks items that fall under it.

    :param :class:`io.StringIO` file: The file to read from
    :param :class:`_sre.SRE_Pattern` until_pattern: A pattern to look for.
        When this pattern is encountered, parsing stops.
    :param bool or_eof: If reading until the end of the file (without
        the pattern having been encountered) is acceptable
    :param bool inclusive: Whether to include the line at the stopping
        point, i.e. the one containing the pattern.
    :param int starting_position: Buffer position to start reading the
        input file from.
    :param function of_type: Get only task items that match this type. This
        argument should be a predicate function that returns true or
        false based on a type determination on the argument.
    """
    if not of_type:
        of_type = lambda x: True
    items = [item for item in _read_items(file) if of_type(item)]
    return items


@contain_file_mutation
def partition_at(file, pattern, or_eof=False, inclusive=False):
    contents, complement = make_file(), make_file()
    line = file.readline()
    while line:
        if not pattern.search(line):
            contents.write(line)
            line = file.readline()
            continue
        if inclusive:
            contents.write(line)
        else:
            complement.write(line)
        break
    if not line and not or_eof:
        raise ValueError("Pattern {} not found in file!".format(pattern))
    complement.write(file.read())

    return contents, complement


@contain_file_mutation
def read_section(file, section):
    pattern = get_section_pattern(section)
    complement = make_file()
    try:
        before, remaining = partition_at(file, pattern, inclusive=True)
        complement.write(before.read())
        contents, after = partition_at(
            remaining, SECTION_OR_EOF_PATTERN, or_eof=True
        )
    except ValueError:
        raise

    if contents.getvalue():
        # if there is a blank line at the end of the section, treat it
        # as a section separator and don't include it in the secion.
        # Note: This should eventually be unnecessary if we introduce
        # higher-level abstractions with different low-level
        # (e.g. file-based) representations, such that the entities
        # are reasoned about at different levels and their file
        # representation is modulated as a side-effect in a
        # deterministic ("monadic") way
        lines = contents.readlines()
        penultimate_line = lines[-1]
        if is_section_separator(penultimate_line):
            complement.write(penultimate_line)
            contents = make_file("".join(lines[:-1]))
    complement.write(after.read())
    return contents, complement


@contain_file_mutation
def add_to_section(file, section, tasks, above=True, ensure_separator=False):
    """ Find a given section in a file and insert tasks into it.  The new tasks
    can be added either at the top or bottom of the section, and any
    pre-existing contents of the section are preserved alongside the new
    additions.
    """

    try:
        contents, complement = read_section(file, section)
    except ValueError:
        raise
    if not contents.getvalue():
        # "base case"
        pattern = get_section_pattern(section)
        try:
            before, remaining = partition_at(file, pattern, inclusive=True)
        except ValueError:
            raise
        new_file = make_file()
        new_file.write(before.read())
        new_file.write(tasks)
        if (
            ensure_separator
            and not is_section_separator(make_file(tasks).readlines()[-1])
            and remaining.getvalue()
            and not is_section_separator(copy_file(remaining).readlines()[0])
        ):
            # in extracting the section from the original file, we disregarded
            # a section separator (if present). Add it back here. (ideally this
            # level of management should be made unnecessary with higher-level
            # abstractions)
            new_file.write(SECTION_SEPARATOR)
        new_file.write(remaining.read())
        return new_file
    else:
        new_contents = make_file()
        if above:
            new_contents.write(tasks)
            new_contents.write(contents.read())
        else:
            new_contents.write(contents.read())
            new_contents.write(tasks)
        return add_to_section(
            complement,
            section,
            new_contents.getvalue(),
            above,
            ensure_separator,
        )