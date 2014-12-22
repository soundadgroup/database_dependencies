#/usr/bin/python2.4
#
#
import re, os, codecs, sys, shutil



def foundString(foundObj):
    if(type(foundObj).__name__ == 'SRE_Match'):
        return foundObj.group() 
    else:
        return ''

# create DATAchunk counters
stripName = re.compile('(.*--?)\n')
stripParams = re.compile('(\(.*?\))[;|$|\sRETURNS]',re.DOTALL)
# THE from-dump object class
servdir = 'C:\\dev\\w4\\app\\w4admin\\services';
allServices = []
def getServices():
    for obj in os.walk(servdir):
        for filenames in obj:
            for fl in filenames:
                fl = str(fl)
                if((fl.find('.php') > -1) and (fl != 'Sproc.php')):
                    with open(servdir+'\\'+fl,encoding="utf-8") as fp:
                        contents = fp.read()
                        allServices.append(sobj(fl,contents))
                    fp.close();

class sobj:
    def __init__(self,sfl,sdef):
        self.fl = sfl
        self.name = foundString(re.search("protected \$name.+'([a-zA-Z_]+)?'",sdef,re.DOTALL))
        self.sproc_suffix = foundString(re.search("protected \$suffix.+'([a-zA-Z_]+)?'",sdef,re.DOTALL))
        self.sproc_names = []
        self.type = ''
        if(len(self.name)>0):
            self.type = 'FUNCTION'
            if(self.sproc_suffix.lower()=='true'):
                self.sproc_names.append(self.name+'_create')
                self.sproc_names.append(self.name+'_get')
                self.sproc_names.append(self.name+'_update')
                self.sproc_names.append(self.name+'_delete')
            else:
                self.sproc_names.append('create_'+self.name)
                self.sproc_names.append('get'+self.name)
                self.sproc_names.append('update_'+self.name)
                self.sproc_names.append('delete_'+self.name)
        else:
            self.table  = foundString(re.search("protected \$_tableName[ =]+'([a-zA-Z_]+)?';",sdef,re.DOTALL))
            if(len(self.table)>0):
                self.type += ' TABLE'
            
            self.view = foundString(re.search("protected \$_viewName[ =]+'([a-zA-Z_]+)?'",sdef,re.DOTALL))
            if(len(self.view)>0):
                self.type += ' VIEW'

        self.in_use = foundString(re.search("//in use",sdef,re.DOTALL))
        #print(self.table + '  '+ self.view +'           '+self.type+': ' + self.fl )
        print(self.in_use+': ' + self.fl +'   ' +self.type)



quit();