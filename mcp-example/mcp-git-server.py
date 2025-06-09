from typing import Any
from mcp.server.fastmcp import FastMCP
from datetime import date
from git import Git

mcp = FastMCP("git")

repo_directory = './defects4j'

@mcp.tool()
def list_commits_between(start_date: date, end_date: date) -> str:
    """ Returns the messages of the commits from an interval between dates.
    Args:
        start_date: The start of the interval.
        end_date: The end of the date.
    """
    repo = Git(repo_directory)
    logs = repo.log('--since={:%Y-%m-%d}'.format(start_date), '--until={:%Y-%m-%d}'.format(end_date), '--oneline')
    return logs

@mcp.tool()
def list_commits_from(contributor: str) -> str:
  """ Returns the commits from a specific contributor.
  Args:
      contributor: The name of the contributor.
  """
  repo = Git(repo_directory)
  logs = repo.log('--author={}'.format(contributor))
  return logs


if __name__ == "__main__":
   print('Initializing server...')
   mcp.run(transport='stdio')