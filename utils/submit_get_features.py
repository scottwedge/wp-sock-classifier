#!/usr/bin/env python

"""Submit a get_features job to the execution grid.  This will create a
per-job directory (and print its name so you can find it) .  Within
that directory will be several files:

  job.bash:  the job control file, used by jsub.

  jsub.{out,err}: output of the jsub command.

  get_features.{out,err}: output of the grid job itself.

The .err files should all be empty.  If not, you should investigate
what went wrong.

"""

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import textwrap

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    args = parser.parse_args()

    job_name = 'get_features.%s' % datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')

    # You'll likely want to customize base_dir.
    base_dir = Path.home() / 'sock-classifier'
    input_file = Path(args.input_file)
    if not input_file.is_absolute():
        print('input_file (%s) must be an absolute path' % input_file, file=sys.stderr)
        sys.exit(1)
    
    job_dir = base_dir / 'jobs' / job_name
    job_dir.mkdir()

    job_template = textwrap.dedent('''\
    #!/bin/bash

    source %(base_dir)s/env/bin/activate

    %(base_dir)s/src/utils/get_features.py \\
      --job-name=%(job_name)s \\
      --log=%(job_dir)s/get_features.log \\
      --progress=1000 \\
      < %(input_file)s
    ''')
    job_file = job_dir / 'job.bash'
    job_file.write_text(job_template % locals())
    job_file.chmod(0o755)

    subprocess.run(['jsub',
                    '-N', str(job_name),
                    '-o', str(job_dir / 'get_features.out'),
                    '-e', str(job_dir / 'get_features.err'),
                    str(job_dir / 'job.bash')],
                   stdout=(job_dir / 'jsub.out').open('w'),
                   stderr=(job_dir / 'jsub.err').open('w')
                   )
    
    print('job directory is', job_dir)


if __name__ == '__main__':
    main()
