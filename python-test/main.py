import actions_toolkit.core  as core

import rich
rich.inspect(core)
rich.print(core)

core.save_state('time', 'new Date().toTimeString()')
core.set_output('result', 'This is the result')
core.info('Something went OK')


from github import Github
from actions_toolkit.github import Context

context = Context()

# First create a Github instance:
g = Github(os.environ['GITHUB_TOKEN'])

# Then play with your Github objects:
repo = g.get_repo("efcs/action")


check_run = repo.create_check_run(name="My Check Run",
                                  head_sha=context.sha,
                                  status="completed",
                                  conclusion="success",
                                  output={"title": "Check Run Output",
                                           "summary": "Check run summary",
                                           "text": "Check run detailed output"})