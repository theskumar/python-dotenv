import os
import sys
import warnings
from collections import OrderedDict

def load_dotenv(dotenv_path):
    """
    Read a .env file and load into os.environ.
    """
    if not os.path.exists(dotenv_path):
        warnings.warn("can't read %s - it doesn't exist." % dotenv_path)
        return None
    for k, v in parse_dotenv(dotenv_path):
        os.environ.setdefault(k, v)
    return True


def read_dotenv(dotenv_path=None):
    """
    Prior name of load_dotenv function.

    Deprecated and pending removal
    
    If not given a path to a dotenv path, does filthy magic stack backtracking
    to find manage.py and then find the dotenv.
    """    
    warnings.warn("read_dotenv deprecated, use load_dotenv instead")
    if dotenv_path is None:
        warnings.warn("read_dotenv without an explicit path is deprecated and will be removed soon")
        frame = sys._getframe()
        dotenv_path = os.path.join(os.path.dirname(frame.f_back.f_code.co_filename), '.env')    
    return load_dotenv(dotenv_path)


def get_key(dotenv_path, key_to_get):
    """
    Gets the value of a given key from the given .env 
    
    If the .env path given doesn't exist, fails
    """    
    key_to_get = str(key_to_get)
    if not os.path.exists(dotenv_path):
        warnings.warn("can't read %s - it doesn't exist." % dotenv_path)
        return None
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    if dotenv_as_dict.has_key(key_to_get):
        return dotenv_as_dict[key_to_get]
    else:
        warnings.warn("key %s not found in %s." % (key_to_get, dotenv_path))
        return None
    
        
def set_key(dotenv_path, key_to_set, value_to_set):
    """
    Adds or Updates a key/value to the given .env 
    
    If the .env path given doesn't exist, fails instead of risking creating
    an orphan .env somewhere in the filesystem 
    """
    key_to_set = str(key_to_set)
    value_to_set = str(value_to_set).strip("'").strip('"')
    if not os.path.exists(dotenv_path):
        warnings.warn("can't write to %s - it doesn't exist." % dotenv_path)
        return None
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    dotenv_as_dict[key_to_set] = value_to_set
    success = flatten_and_write(dotenv_path, dotenv_as_dict)
    return success, key_to_set, value_to_set


def unset_key(dotenv_path, key_to_unset):
    """
    Removes a given key from the given .env 
    
    If the .env path given doesn't exist, fails
    If the given key doesn't exist in the .env, fails 
    """
    key_to_unset = str(key_to_unset)
    if not os.path.exists(dotenv_path):
        warnings.warn("can't delete from %s - it doesn't exist." % dotenv_path)
        return None
    dotenv_as_dict = OrderedDict(parse_dotenv(dotenv_path))
    if dotenv_as_dict.has_key(key_to_unset):
        dotenv_as_dict.pop(key_to_unset, None)
    else: 
        warnings.warn("key %s not removed from %s - key doesn't exist." % (key_to_unset, dotenv_path))
        return None
    success = flatten_and_write(dotenv_path, dotenv_as_dict)
    return success, key_to_unset 


def parse_dotenv(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip("'").strip('"')
            yield k, v
        

def flatten_and_write(dotenv_path, dotenv_as_dict):
    with open(dotenv_path, "w") as f:
        for k, v in dotenv_as_dict.items():
            f.write('%s="%s"\r\n' % (k, v))
    return True
            
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="the absolute path of the .env file you want to use")
    parser.add_argument("action", help="what you want to do with the .env file (get, set, unset)", nargs='?')
    parser.add_argument("key", help="the environment key you want to set", nargs='?')
    parser.add_argument("value", help="the value you want to set 'key' to", nargs='?')
    parser.add_argument("--force", help="force writing even if the file at the given path doesn't end in .env")
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        warnings.warn("there doesn't appear to be a file at %s" % args.file_path)
        exit(1)
    if not args.force:
        if not args.file_path.endswith(".env"):
            warnings.warn("the file %s doesn't appear to be a .env file, use --force to proceed" % args.file_path)
            exit(1)
      
    if args.action == None:
        with open(args.file_path) as f:
            print f.read()
        exit(0)    
    elif args.action == "get":
        stored_value = get_key(args.file_path, args.key)
        if stored_value != None:
            print(args.key)
            print(stored_value)
        else:
            exit(1)
    elif args.action == "set":
        success, key, value = set_key(args.file_path, args.key, args.value)
        if success != None:
            print("%s: %s" % (key, value))
        else:
            exit(1)
    elif args.action == "unset":
        success, key = unset_key(args.file_path, args.key)
        if success != None:
            print("unset %s" % key)
        else:
            exit(1)
    # Need to investigate if this can actually work or if the scope of the new environ variables
    # Expires when python exits
    #
    # elif args.action == "load":
    #     success = load_dotenv(args.file_path)
    #     if success != None:
    #         print("loaded %s into environment" % args.file_path)
    #     else:
    #         exit(1)
    exit(0)