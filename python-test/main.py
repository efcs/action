import actions_toolkit.core  as core

import rich
rich.inspect(core)
rich.print(core)

core.error('Something went wrong.')
core.save_state('time', 'new Date().toTimeString()')
core.set_output('result', 'This is the result')
core.info('Something went OK')
core.set_failed('This went wrong.')
