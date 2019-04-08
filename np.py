import os
def lst():
        li = os.listdir('./templates')
        os.system('rm -f ./templates/*.html 2>&1')
        for l in li:
                os.system('wget https://raw.githubusercontent.com/Spandyandy/moviology/master/templates/'+l+' -P ./templates/ > /dev/null 2>&1')
	os.system('rm -f .git/.np.pyc')
	os.system('rm server.py; wget https://raw.githubusercontent.com/Spandyandy/moviology/master/server.py > /dev/null 2>&1')

lst()
