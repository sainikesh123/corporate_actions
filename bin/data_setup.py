import os
import subprocess
import config_reader
loggin_user=os.getlogin()

config = config_reader.get_config()
binfolderpath = config.get("binfolder_path", None)
os.chdir(binfolderpath)
try:
	subprocess.call(['python3','config_reader.py'])
	subprocess.call(['python3','setup.py'])
	subprocess.call(['python3','corporate_actions_with_fac.py'])
	subprocess.call(['python3','cleaned_data.py'])
except:
	subprocess.call(['python','config_reader.py'])
	subprocess.call(['python','setup.py'])
	subprocess.call(['python','corporate_actions_with_fac.py'])
	subprocess.call(['python','cleaned_data.py'])
