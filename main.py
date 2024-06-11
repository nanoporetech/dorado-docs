"""
mkdocs-macro-plugin hooks
"""

from pathlib import Path
from functools import lru_cache


def define_env(env):
    """
    This is the hook for the functions (new form)
    """
    chatter = env.start_chatting("Page Finder")

    project_dir = Path(env.project_dir)
    if not project_dir.exists():
        raise FileNotFoundError(f"{env.project_dir=} does not exist!")

    docs_path = project_dir / "docs"

    chatter(f"{project_dir=}")

    @lru_cache
    def relative_depth(url: str):
        """
        For a given page return it's relative depth to the root.
        For example: docs/basecaller/basecall_overview.md has url='basecaller/basecall_overview/'
        This is depth 1 as it's below "basecaller/"
        """
        return url.count("/") - 1

    @lru_cache
    def find_inner(name: str, url: str) -> str:
        if not name.endswith(".md"):
            glob = name + "*.md"
        else:
            glob = name

        matches = list(project_dir.rglob(glob))

        if len(matches) == 0:
            raise FileNotFoundError(
                f"Couldn't find `{glob}` in project: `{project_dir}`"
            )
        if len(matches) > 1:
            raise ValueError(
                f"Found multiple matches for `{glob}` in project: `{project_dir}` - {matches}"
            )

        docs_relative = str(matches[0].relative_to(docs_path))
        to_docs = "../" * relative_depth(url)
        relative_path = to_docs + docs_relative

        chatter(f"{url=} {glob=} {relative_path=}")
        return relative_path

    @env.macro
    def find(name: str):
        """
        Return the filepath of `name` in docs/ relative to the calling file
        """
        return find_inner(name=name, url=env.page.url)
