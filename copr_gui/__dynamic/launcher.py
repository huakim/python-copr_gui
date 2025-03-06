import sys
from copr import v3
import argparse
import os

from . import uistatusbar as wx
from .monitor_helper import run_monitor as runMonitor
from .packages_monitor import PackagesMonitor
from .projects_monitor import ProjectsMonitor
from .project_chroots_monitor import ProjectChrootsMonitor
from .builds_monitor import BuildsMonitor, BuildChrootsMonitor

DEFAULT_CONFIG = os.path.expanduser("~/.config/copr")

def run(function, configfile, *args):
    app = wx.CreateApp()
    from copr.v3 import Client
    client = Client.create_from_config_file(configfile)
    frame = function(None, (client, *args))
    frame.app = app
    return frame

def run_Projects(config, ownername):
    return run(ProjectsMonitor, config, ownername)

def run_Builds(config, ownername, projectname):
    return run(BuildsMonitor, config, ownername, projectname)

def run_Packages(config, ownername, projectname):
    return run(PackagesMonitor, config, ownername, projectname)

def run_Project_Chroots(config, ownername, projectname):
    return run(ProjectChrootsMonitor, config, ownername, projectname)

def run_Build_Chroots(config, build):
    return run(BuildChrootsMonitor, config, build)

def startcli(args=None, default_icon=''):
    # Create the top-level parser
    parser = argparse.ArgumentParser(prog='launcher', description='Command line launcher with tree subcommands')
    parser.add_argument('--iconpath', default=default_icon, help='Icon path')
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # Create the 'builds' subcommand parser
    builds_parser = subparsers.add_parser('builds', help='Manage builds')
    builds_parser.add_argument('--config', default=DEFAULT_CONFIG, help='Configuration file path')
    builds_parser.add_argument('--ownername', required=True, help='Owner name')
    builds_parser.add_argument('--projectname', required=True, help='Project name')

    # Create the 'builds' subcommand parser
    build_chroots_parser = subparsers.add_parser('buildchroots', help='Manage build chroots')
    build_chroots_parser.add_argument('--config', default=DEFAULT_CONFIG, help='Configuration file path')
    build_chroots_parser.add_argument('--id', required=True, help='Build id')

    # Create the 'projects' subcommand parser
    projects_parser = subparsers.add_parser('projects', help='Manage projects')
    projects_parser.add_argument('--config', default=DEFAULT_CONFIG, help='Configuration file path')
    projects_parser.add_argument('--ownername', required=True, help='Owner name')

    # Create the 'packages' subcommand parser
    packages_parser = subparsers.add_parser('packages', help='Manage packages')
    packages_parser.add_argument('--config', default=DEFAULT_CONFIG, help='Configuration file path')
    packages_parser.add_argument('--ownername', required=True, help='Owner name')
    packages_parser.add_argument('--projectname', required=True, help='Project name')


    # Create the 'packages' subcommand parser
    packages_parser = subparsers.add_parser('projectchroots', help='Manage project chroots')
    packages_parser.add_argument('--config', default=DEFAULT_CONFIG, help='Configuration file path')
    packages_parser.add_argument('--ownername', required=True, help='Owner name')
    packages_parser.add_argument('--projectname', required=True, help='Project name')
    # Parse the command line arguments
    args = parser.parse_args(args)
    frame = None
    # Process the subcommands and options
    if args.subcommand == 'builds':
        print(f"Builds subcommand: config={args.config}, ownername={args.ownername}, projectname={args.projectname}")
        frame = run_Builds(args.config, args.ownername, args.projectname)
    elif args.subcommand == 'projects':
        print(f"Projects subcommand: config={args.config}, ownername={args.ownername}")
        frame = run_Projects(args.config, args.ownername)
    elif args.subcommand == 'packages':
        print(f"Packages subcommand: config={args.config}, ownername={args.ownername}, projectname={args.projectname}")
        frame = run_Packages(args.config, args.ownername, args.projectname)
    elif args.subcommand == 'projectchroots':
        print(f"ProjectChroots subcommand: config={args.config}, ownername={args.ownername}, projectname={args.projectname}")
        frame = run_Project_Chroots(args.config, args.ownername, args.projectname)
    elif args.subcommand == 'buildchroots':
        print(f"BuildChroots subcommand: config={args.config}, id={args.id}")
        frame = run_Build_Chroots(args.config, args.id)
    else:
        frame = run_Projects(DEFAULT_CONFIG, None)
    if not frame is None:
        ICON_PATH = args.iconpath
        if os.path.exists(ICON_PATH):
            # #frame.SetIcon(wx.Icon(ICON_PATH, wx.BITMAP_TYPE_ICO))
            frame.SetIconFromPath(ICON_PATH)
          #  frame.app.SetTopWindow(frame)
        else:
            print('you forgot to provide right path to icon')
        frame.Show()
        wx.InitApp(frame.app)

def main(*args, **kwargs):
    try:
        startcli(*args, **kwargs)
    except Exception as e:
        wx.error(str(e), type(e).__name__, parent)

def __test():
    main()

