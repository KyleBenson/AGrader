# Agrader driver from ICS 23 Fall 2012

from os import listdir, system, getcwd, chdir, getcwd, walk
from os.path import isdir, join, split, exists
import sys

classpath_sep = ':'

def ReadConfig(project_dir):
    sys.path.append(project_dir)
    import project_config
    return project_config.Config(project_dir)

def ICS23Agrader(args):
    config = ReadConfig(args.dir)

    for (dirpath, dirnames, filenames) in walk(join(args.dir, 'submissions')):

        if len(dirnames) > 0 or not (f.endswith('.java') for f in filenames) or dirpath.endswith('removed'):
            continue
        
        for f in filenames:
            print dirpath + f + ':'

        print config.classpath
        dirname = split(dirpath)[-1]
        main_class = config.main_classes[dirname]
        
        system('javac -cp %s %s' % (dirpath + classpath_sep + config.classpath, join(dirpath, main_class + '.java')))

        for cmd_inputs in [join(args.dir, cmd_input) for cmd_input in config.cmd_inputs[dirname]]:
            print 'Running %s with inputs:\n%s' % (main_class, cmd_inputs)
            temp_inputs_file = join(args.dir, 'inputs.tmp')

            with open(temp_inputs_file, 'w') as f:
                f.write(cmd_inputs)

            system('java -cp %s %s < %s' % (dirpath + classpath_sep + config.classpath, main_class, temp_inputs_file))

        #give option for viewing source code
        if raw_input("View source files? y/n? ") == 'y':
            system('find ' + dirpath + ' \( -iname "*.java" \) -exec less \'{}\' +') # \'!\' -name Smiley.java \'!\' -name MusicArchive.java 
