#!/usr/bin/env python
import os
import platform

import click

from composer.utils import display_message
from composer.backend.filesystem.primitives import bare_filename

# TODO: need to improve this script to do regex matching on wiki page names,
# and sort the pages by type and in chronological order + Misc/uncategorized

INDEXFILE = "pages"
INDEXTITLE = "index"


def is_wiki(filename):
    return filename[-5:] == ".wiki"


def get_files(path, of_type=None):
    """ Get all files at the specified path of the specified type.

    :param str path: The location of the wiki
    :returns list: Only the wiki files, with extensions truncated
    """
    files = os.listdir(path)
    if of_type:
        files = filter(of_type, files)
    files = [os.path.join(path, f) for f in files]
    return files


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def sort_alphabetically(files):
    return sorted(files)


def sort_by_date_modified(files):
    return sorted(files, key=os.path.getmtime)


def sort_by_date_created(files):
    return sorted(files, key=creation_date)


def format_for_display(files):
    filenames = map(bare_filename, files)
    filenames = ["\t* [[" + page + "]]\n" for page in filenames]
    return filenames


def update_index(path, filename=None, title=None):
    """ Generate the index from all .wiki files present at the provided
    path. Use the provided filename and title string, if any, or use defaults.
    This generates the index from scratch and overwrites any existing index
    files that may be present. It generates a root index linking to actual
    index files, each of which are sorted according to different criteria.

    :param str path: The location of the wiki
    :param str filename: The filename (not including extension) to use when
        saving the generated index
    :param str title: A title string to use at the top of the file
    """
    if not filename:
        filename = INDEXFILE
    if not title:
        title = INDEXTITLE
    files = get_files(path, is_wiki)
    files_alphabetical = sort_alphabetically(files)
    files_by_date_modified = sort_by_date_modified(files)
    files_by_date_created = sort_by_date_created(files)
    files_alphabetical, files_by_date_modified, files_by_date_created = (
        format_for_display(files_alphabetical),
        format_for_display(files_by_date_modified),
        format_for_display(files_by_date_created),
    )
    indexes = {
        'alphabetical': files_alphabetical,
        'by date modified': files_by_date_modified,
        'by date created': files_by_date_created,
    }
    root_entries = []
    for name in indexes.keys():
        root_entries += (
            "\t* [[{prefix}_{name}|{name}]]\n".format(prefix=filename.capitalize(), name=name.capitalize())
        )
    root_filename = os.path.join(path, "{}.wiki".format(filename))
    root_title = "= {} =".format(title).upper()
    # write main index file
    write_index(root_filename, root_title, root_entries)
    # print "%d wiki pages found: %s" % (len(wikipages), str(wikipages))
    for k, v in indexes.items():
        index_filename = os.path.join(path, "{prefix}_{name}.wiki".format(prefix=filename, name=k))
        index_title = "= {} =".format(title).upper()
        write_index(index_filename,
                    index_title,
                    v)


def write_index(path_to_file, title, entries):
    """ Write an index file at the given path, with the given title and
    contents.

    :param str path_to_file: The path to the index file
    :param str title: A title string to use at the top of the file
    :param list entries: A list of entries to be written as the contents
        of the index file.
    """
    with open(path_to_file, "w") as f:
        f.write(title + "\n")
        for page in entries:
            f.write(page)


@click.command(
    help=(
        'Regenerate the index for the wiki at the indicated path. '
        'This will result in any newly created pages being included in '
        'the index.\n'
    )
)
@click.argument("wikipath")
@click.option(
    "-f",
    "--filename",
    help=("Filename to use for the index (default '{}').".format(INDEXFILE)),
)
@click.option(
    "-t",
    "--title",
    help=("Title for the index page (default '{}')".format(INDEXTITLE)),
)
def main(wikipath, filename=None, title=None):
    wikipath = wikipath.rstrip("/")
    display_message()
    display_message(">>> Operating on wiki at location: %s <<<" % wikipath)
    display_message()

    update_index(wikipath, filename, title)
