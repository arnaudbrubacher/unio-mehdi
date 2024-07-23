import os
import sys
import argparse
import pathlib

############################################################################
def main(**args):
    root_path = str(pathlib.Path(__file__).parent.resolve())

    # log_path = os.path.join(root_path, "log")
    # if not os.path.exists(log_path):
    #     os.makedirs(log_path)
    # setup_logger(log_path, conf["id"])


    if "'run'" in args['commands']:
        print("[[RUN]]")

    if "'deploy'" in args['commands']:
        print("[[DEPLOY]]")

    if "'migrate'" in args['commands']:
        print("[[migrate]]")

    if "'makemigrations'" in args['commands']:
        print("[[makemigrations]]")

        # s1_compile_client_project(root_path)



############################################################################33
if __name__ == '__main__':
    defined_commands = ["run", "deploy", "migrate", "makemigrations"]
    
    parser = argparse.ArgumentParser(description='UNIO Admin Script')
    parser.add_argument('-c', dest='commands', type=ascii, nargs='+',
                         default='run',help='list of commands to execute.')

    args = parser.parse_args()
    main(**vars(args))
############################################################################