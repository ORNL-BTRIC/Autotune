import ConfigParser
import shutil
import sys
import os
import fileinput

def replace_in_file(file_path, pattern, subst):
    for line in fileinput.input(file_path, inplace=True):
        line = line.replace(pattern, subst)
        print line,

def recursive_overwrite(src, dest):
    if os.path.isdir(src):
        if not os.path.exists(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        for f in files:
            recursive_overwrite(os.path.join(src, f), 
                                os.path.join(dest, f))
    else:
        shutil.copyfile(src, dest)


def main():
    print "Starting installation of Autotune"
    confParser = ConfigParser.ConfigParser()

    if confParser.read('install-settings.ini') != []:
        # derive install location root path
        rootpath = os.path.join(confParser.get('Paths', 'www_path'), 'autotune')

        # create install location root path
        if not os.path.exists(rootpath):
            os.makedirs(rootpath)

        # copy directories to correct location
        srcdirs = ['backend', 'frontend', 'service']
        for srcdir in srcdirs:
            src = os.path.join(os.path.realpath(confParser.get('Paths', 'src_dir')), srcdir)
            dest = os.path.join(rootpath, srcdir)
            try:
                print "Copying %s to %s" % (src, dest)
                recursive_overwrite(src, dest)
            except:
                print "Error:", sys.exc_info()[0]

        # Apply modifications to files
        # Update the WSDL
        print "Applying modifications to files"

        # For files in /service
        
        # Update WSDL
        replace_in_file(os.path.join(rootpath, 'service', 'autotune.wsdl'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))

        # Update MySQL settings
        replace_in_file(os.path.join(rootpath, 'service', 'dbAccess.php'),
                        'autotune_host',
                        confParser.get('MySQL', 'mysql_host'))

        replace_in_file(os.path.join(rootpath, 'service', 'dbAccess.php'),
                        'autotune_db',
                        confParser.get('MySQL', 'mysql_db'))

        replace_in_file(os.path.join(rootpath, 'service', 'dbAccess.php'),
                        'autotune_user',
                        confParser.get('MySQL', 'mysql_user'))

        replace_in_file(os.path.join(rootpath, 'service', 'dbAccess.php'),
                        'autotune_password',
                        confParser.get('MySQL', 'mysql_password'))
                        
        replace_in_file(os.path.join(rootpath, 'service', 'example', 'pyClient.py'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name')) 
        
        replace_in_file(os.path.join(rootpath, 'service', 'example', 'pyClient.py'),
                        'youremail',
                        confParser.get('Contact', 'email'))
        

        # For files in /frontend
        
        replace_in_file(os.path.join(rootpath, 'frontend', 'contactRequest.php'),
                        'youremail',
                        confParser.get('Contact', 'email'))

        # TODO: ip2latlon.php; add the echo

        replace_in_file(os.path.join(rootpath, 'frontend', 'iptolatlng.php'),
                        'yourapikey',
                        confParser.get('API Key', 'google_api_key'))

        replace_in_file(os.path.join(rootpath, 'frontend', 'selectingModelPage.php'),
                        'yourapikey',
                        confParser.get('API Key', 'google_api_key'))
        
        replace_in_file(os.path.join(rootpath, 'frontend', 'paramGen.php'),
                        'yourserverpath',
                        confParser.get('Paths', 'www_path'))

        replace_in_file(os.path.join(rootpath, 'frontend', 'statusProgress.php'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))
        
        replace_in_file(os.path.join(rootpath, 'frontend', 'statusUpdate.php'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))

        replace_in_file(os.path.join(rootpath, 'frontend', 'trackingProgress.php'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))

        replace_in_file(os.path.join(rootpath, 'frontend', 'tune.php'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))
        # Update the javascript files
        replace_in_file(os.path.join(rootpath, 'frontend', 'jquery', 'JQContact.js'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))
        replace_in_file(os.path.join(rootpath, 'frontend', 'jquery', 'JQProgress.js'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))


        # For files in /backend
        # Update settings for the autotune service
        # 1. Linux only:
        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.conf'),
                        'system_username',
                        confParser.get('System Service', 'system_username'))
        
        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.conf'),
                        'system_gid',
                        confParser.get('System Service', 'system_gid'))
        
        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.conf'),
                        'execlocation',
                        os.path.join(rootpath, 'backend', 'autotune.py'))

        # 2. Windows/MacOS: TODO

        # In file autotune.py, update MySQL settings
        # Update MySQL settings
        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.py'),
                        'autotune_host',
                        confParser.get('MySQL', 'mysql_host'))

        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.py'),
                        'autotune_db',
                        confParser.get('MySQL', 'mysql_db'))

        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.py'),
                        'autotune_user',
                        confParser.get('MySQL', 'mysql_user'))

        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.py'),
                        'autotune_password',
                        confParser.get('MySQL', 'mysql_password'))

        # Update domain name
        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.py'),
                        'yourdomain.com',
                        confParser.get('WSDL', 'domain_name'))

        # TODO: update energyplus location files
        # TODO: remove autotune.roofcalc.com update code Line 1242
        # TODO: remove gmail stuff

        # Update SMTP
        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.py'),
                        'smtpserver',
                        confParser.get('Contact', 'SMTP'))
        
        replace_in_file(os.path.join(rootpath, 'backend', 'autotune.py'),
                        'youremail',
                        confParser.get('Contact', 'email'))
        
        
        print "This section is complete. Please proceed to next steps in the README."
    else:
        print "Error: Could not read install-settings.ini file"


if __name__ == "__main__":
    main()



