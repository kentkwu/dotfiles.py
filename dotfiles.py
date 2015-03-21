#!/usr/bin/env python
import argparse
import os
import shutil
import errno
import sys

def copy(dotfile, home_dir, backups_dir):
    """Copies the dotfile to the the dotfiles_backup directory"""
    print 'Copying {} from home directory to {}'.format(dotfile, backups_dir)
    try:
        shutil.copy2('{}/.{}'.format(home_dir, dotfile), '{}/.{}'.format(backups_dir, dotfile))
    except IOError as e:
        if e.errno == errno.EISDIR:
            shutil.copytree('{}/.{}'.format(home_dir, dotfile), '{}/.{}'.format(backups_dir, dotfile))
        else:
            raise
    print 'Success'

def move(dotfile, home_dir, dotfiles_dir):
    """Moves the dotfile from the home directory to the dotfiles directory"""
    print 'Moving {} from home directory to {}'.format(dotfile, dotfiles_dir)
    shutil.move('{}/.{}'.format(home_dir, dotfile), '{}/{}'.format(dotfiles_dir, dotfile))
    print 'Success'

def symlink(dotfile, home_dir, dotfiles_dir):
    """Creates a symlink in the home directory for a dotfile in ~/dotfiles"""
    print 'Creating symlink in home directory for {}'.format(dotfile)
    source = '{}/{}'.format(dotfiles_dir, dotfile)
    dest = '{}/.{}'.format(home_dir, dotfile)
    try:
        os.symlink(source, dest)
        print "Success"
    except OSError as e:
        if e.errno == errno.EEXIST:
            print "{} already exists in the home directory".format(dotfile)
        else:
            raise

def symlink_to_dotfile(dotfile, dotfiles_dir, home_dir):
    """Deletes the symlink for a dotfile in the home directory, and move the dotfile from ~/dotfiles
       to the home directory"""
    symlinkpath = '{}/.{}'.format(home_dir, dotfile)
    if not os.path.islink(symlinkpath):
        print "{} is not a symlink in {}".format(dotfile, home_dir)
    else:
        print "Removing {} symlink from home directory".format(dotfile)
        os.remove('{}/.{}'.format(home_dir, dotfile))
        print "Success"
        print "Moving {} from {} to {}".format(dotfile, dotfiles_dir, home_dir)
        shutil.move('{}/{}'.format(dotfiles_dir, dotfile), '{}/.{}'.format(home_dir, dotfile))
        print "Success"

def repo_to_symlink(dotfile, dotfiles_dir, home_dir):
    """Creates a symlink in the home directory for a dotfile in ~/dotfiles"""
    symlink(dotfile, HOMEDIR, DOTFILES)

def get_all(directory):
    """Returns a list of all of the files in a directory"""
    files = os.listdir(directory)
    return files

def importall(dotfiles_dir, home_dir):
    """Create symlinks for all dotfiles in dotfiles directory in the home directory"""
    DOTFILES = os.listdir(dotfiles_dir)
    for file in get_all(dotfiles_dir):
        symlink(file, home_dir, dotfiles_dir)

def symlinks_to_dotfiles_all(dotfiles_dir, home_dir):
    """Changes all symlinks in the home directory back to dotfiles"""
    for file in get_all(dotfiles_dir):
        reverse(file, dotfiles_dir, home_dir)

def removeitem(itempath):
    """Removes an item given a path as an argument. If the item is a directory, remove it recursively"""
    try:
        os.remove(itempath)
    except OSError as e:
        if e.errno == errno.EPERM:
            shutil.rmtree(itempath)
        else:
            raise

def add_to_backups(list_of_files):
    """Add a list of files to the backups file. Old files are overwritten"""
    if os.path.exists(BACKUPS) == False:
        print "Creating {}".format(BACKUPS)
        os.mkdir(BACKUPS, 0755)
    else:
        confirmation = ''
        while (confirmation != 'y' and confirmation != 'n'):
            confirmation = raw_input("This will overwrite the files in {}. Do you still \
                                  want to proceed? (y/n): ".format(BACKUPS))
        if confirmation == 'y':
            for file in list_of_files:
                print '{} from {} to {}'.format(file, HOMEDIR, BACKUPS)
                print 'The sourve file path is {}/.{}'.format(BACKUPS, file)
                if os.path.isdir('{}/.{}'.format(BACKUPS, file)):
                    removeitem('{}/.{}'.format(BACKUPS, file))
                copy(file, HOMEDIR, BACKUPS)
        elif confirmation == 'n':
            print 'Exiting script'
            sys.exit()

def add_to_repo(list_of_files):
    """Add a dotfile in the home directory to the dotfile repo and create a symlink for it"""
    if os.path.exists(DOTFILES) == False:
        print "Creating {}".format(DOTFILES, 0755)
        os.mkdir(DOTFILES)
    for file in list_of_files:
        if not os.path.islink('{}.{}'.format(HOMEDIR, file)):
            move(file, HOMEDIR, DOTFILES)
            symlink(file, HOMEDIR, DOTFILES)
            print "Done"
        else:
            print "{} is already a symlink.".format(file)

def symlinks_to_dotfiles(list_of_files):
    """converts symlinks in home directory back into dot files"""
    for file in args.reverse:
        symlink_to_dotfile(file, DOTFILES, HOMEDIR)

def repo_to_symlinks(list_of_files):
    """Creates a symlink in the home directory for each file in ~/dotfiles specified"""
    for file in list_of_files:
        importdotfile(file, DOTFILES, HOMEDIR)

def repo_to_symlinks_all():
    """Creates symlinks in home directory for every file in dotfiles"""
    for file in get_all(DOTFILES):
        symlink(file, DOTFILES, HOMEDIR)


def remove_all_hidden_symlinks():
    """Removes all hidden symlinks in the home directory"""
    files = get_all(HOMEDIR)
    hidden_symlinks = [file for file in files if file[0] == '.' and os.path.islink('{}/{}'.format(HOMEDIR, file))]
    print "REMOVING SYMLINKS"
    for file in hidden_symlinks:
        os.remove('{}/{}'.format(HOMEDIR, file))
    print "DONE"


if __name__ == "__main__":

    desc = """This is a script to easily manage your important dotfiles through version control (such as git). This script will create a ~/dotfiles folder which will hold all of your selected dotfiles, and a ~/dotfiles_backups which will hold additional backups or your dotfiles. A symlink for each dotfile in ~/dotfiles is created at the top level, which will allow for programs to access them normally."""

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument( '-b', '--backup', nargs='*', help='Copies your selected dotfiles into dotfiles_backups',
                        dest='backup', action='store' )

    parser.add_argument( '-a', '--add', nargs='*', help='Copy dotfiles to ~/dotfiles_backup, move dotfile from \
                                            home directory to ~/dotfiles, and create symlink from home directory', 
                        dest='files', action='store' )

    parser.add_argument( '-r', '--reverse', nargs='*', help='Reverse -a for dotfile(s) in ~/dotfiles',
                        dest='reverse', action='store' )

    parser.add_argument( '--reverseall', help='Convert all symlinks to dotfiles back into dotfiles',
                        dest='reverseall', action='store_true' )

    parser.add_argument( '-i', '--import', nargs='*', help='Create symlink in home directory for dotfile(s) in ~/dotfiles',
                        dest='importfiles', action='store' )

    parser.add_argument( '--importall', help='Create symlinks in home directory for all dotfiles in ~/dotfiles',
                        dest='importall', action='store_true' )

    parser.add_argument( '--removelinks', help="Removes all hidden symlinks in the home directory. DON'T USE THIS IF YOU HAVE OTHER SYMLINKS OTHER THAN YOUR DOTFILES",
                        dest='remove_all_links', action='store_true')

    args = parser.parse_args()

    HOMEDIR = os.path.expanduser('~')
    BACKUPS = os.path.expanduser('~/dotfiles_backups')
    DOTFILES = os.path.expanduser('~/dotfiles')


    if args.importall:
        importall(DOTFILES, HOMEDIR)
    if args.backup:
        add_to_backups(args.backup)
    if args.files:
        add_to_repo(args.files)
    if args.reverse:
        symlinks_to_dotfiles(args.reverse)
    if args.reverseall:
        reverseall(DOTFILES, HOMEDIR)
    if args.importfiles:
        repo_to_symlinks(args.importfiles)
    if args.importall:
        repo_to_symlinks_all()
    if args.remove_all_links:
        remove_all_hidden_symlinks()
    print "Exiting"




