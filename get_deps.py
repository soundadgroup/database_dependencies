#/usr/bin/python2.4
#
#
import re, os, codecs, sys, shutil

servdir = 'C:\\dev\\w4\\app\\w4admin\\services';
schema_only_dbdump = 'data/20141216_ST_schema.sql';

def foundString    (foundObj):
    if(type(foundObj).__name__ == 'SRE_Match'):
        return foundObj.group() 
    else:
        return ''

def splitNameString(nStr,which):
    return foundString(re.search(which+'\:\s(.*?)[$|\n|;]',nStr,re.DOTALL)).replace(';', '').replace(which+': ', '').lstrip().rstrip()
def getServices():
    for obj in os.walk(servdir):
        for filenames in obj:
            for fl in filenames:
                fl = str(fl)
                if((fl.find('.php') > -1) and (fl != 'Sproc.php')):
                    with open(servdir+'\\'+fl,encoding="utf-8") as fp:
                        contents = fp.read()
                        service_list.append(sobj(fl,contents))
                    fp.close();

class sobj:
    def __init__(self,sfl,sdef):
        self.fl = sfl
        self.name = foundString(re.search("protected \$name[ =]+'([a-zA-Z_]+)?'",sdef,re.DOTALL))
        self.name = re.sub(r"protected \$name[ =]+'",'', self.name).replace("'","")
        self.sproc_suffix = foundString(re.search("protected \$suffix[ =]+([a-zA-Z_]+)?",sdef,re.DOTALL))
        self.sproc_suffix = re.sub(r"protected \$suffix[ =]+",'', self.sproc_suffix)       
        self.sproc_names = []
        self.type = ''
        self.view = ''
        self.table = ''
        self.isSproc = False
        if(len(self.name)>0):
            self.type = 'FUNCTION'
            if(self.sproc_suffix=='true'):
                self.sproc_names.append(self.name+'_create')
                self.sproc_names.append(self.name+'_get')
                self.sproc_names.append(self.name+'_get_list')
                self.sproc_names.append(self.name+'_get_count')
                self.sproc_names.append(self.name+'_update')
                self.sproc_names.append(self.name+'_delete')
                self.sproc_names.append(self.name+'_get_summary')
            else:
                self.sproc_names.append('create_'+self.name)
                self.sproc_names.append('get_'+self.name)
                self.sproc_names.append('update_'+self.name)
                self.sproc_names.append('delete_'+self.name)
            self.isSproc = True
        else:
            self.table  = foundString(re.search("protected \$_tableName[ =]+'([a-zA-Z_]+)?'",sdef,re.DOTALL))
            if(len(self.table)>0):
                self.table = re.sub(r"protected \$_tableName[ =]+'",'', self.table).replace("'","")
                self.type += ' TABLE'
            
            self.view = foundString(re.search("protected \$_viewName[ =]+'([a-zA-Z_]+)?'",sdef,re.DOTALL))
            if(len(self.view)>0):
                self.view = re.sub(r"protected \$_viewName[ =]+'",'', self.view).replace("'","")
                self.type += ' VIEW'

        self.in_use = (len(foundString(re.search("//in use",sdef,re.DOTALL)))>0)
        self.in_use = (len(foundString(re.search("//in use",sdef,re.DOTALL)))>0)

class eobj:
    def __init__(self,name,schema,otype):
        self.name = name
        self.schema = schema
        self.type = otype
        self.ok = False
        self.deps = []

class dpObj:
    def __init__(self,entry):
        #grab name definition
        objNameDef = foundString(re.search('(.*?)\n--',entry))
        self.name = splitNameString(objNameDef,'Name')
        self.type = foundString(re.search('Type\:\s(.*?)[$|\n|;]',objNameDef,re.DOTALL)).replace(';', '').replace('Type: ', '')
        #strip out object definition comment
        self.definition = entry.replace(objNameDef,'')
        #only beginning and end have no name 
        self.schema = splitNameString(objNameDef,'Schema')
        self.owner = splitNameString(objNameDef,'Owner')
        self.tablespace = splitNameString(objNameDef,'Tablespace')
        self.in_use = False
        self.engine_use = False
        if (self.name == ''): self.name = 'global'
        if (len(self.type)==''): self.schema = 'global'
        if (len(self.schema)<2): self.schema = 'public'

        if(self.type == 'Comment'):
            self.commentOn = foundString(re.search('[A-Z]*\s(.*?)$',self.name,re.DOTALL))
            self.definition = foundString(re.search('COMMENT.*?;',self.definition,re.DOTALL))
            return
        elif((self.type == 'FK CONSTRAINT') or (type == 'ACL') or (type == 'CONSTRAINT') or (type == 'SEQUENCE')):
            self.definition = foundString(re.search('ALTER.*?;',self.definition,re.DOTALL))
            return

        self.comments = [];
        self.create = foundString(re.search('CREATE.*?;',self.definition,re.DOTALL))
        self.definition = self.definition.replace(self.create,'')
        self.generateDrop()

        if(self.type == 'FUNCTION'):
            self.defineFunction()

        elif(self.type == 'TABLE'):
             self.defineTable()

        elif(self.type == 'TYPE'):
            self.defineType()

        elif(self.type == 'VIEW'):
            self.defineView()

        self.getDependants()
        self.getDependancies()

    def getAlter(self):
        self.params=[]

    def getFunctionParams(self):
        self.paramString = foundString(re.search('(\(.*?\)) RETURNS',self.name))
        if (len(self.paramString)<2):
            self.paramString = foundString(re.search('(\(.*?\))',self.name))
        self.name = (self.name).replace(self.paramString,'')
        paramStringFull = foundString(stripParams.search(self.create))
        self.create = (self.create).replace(paramStringFull,'(#PARAMS#) ')
        self.params = re.split(',[\n|\s]',paramStringFull)
        
        for i in range(0,(len(self.params)-1)):
            self.params[i]=self.params[i].lstrip()
        
        for p in self.params:
            if(p.find("CONSTRAINT ")==0):                
                self.constraints.append(p)
                self.params.remove(p)
    

    def getDependants(self):
        self.dependants = []

    def getDependancies(self):
        self.dependencies = []

    def getIndices(self):
        return dpObjects.index(self)

    def generateDrop(self):
        if (len(self.create)<1):
            self.drop = '' 
            return
        self.drop = 'DROP ' + self.type+' IF EXISTS '
        if((self.type != 'SCHEMA') and (self.type != 'EXTENSION')): self.drop += self.schema+'.'
        self.drop  += self.name
        if hasattr(self, 'paramString'): self.drop += self.paramString
        self.drop +=';'
       
    def defineFunction(self):        
        self.getFunctionParams()
        self.overLoads = []
        #self.getDependancies()
        #self.getDependant()
        self.create = (self.create).replace('CREATE','CREATE OR REPLACE')
        self.returns = self.generateReturn()

    def getTableColumns(self):
        self.columns = []
        self.constraints = []
        #ALTER TABLE foo DROP CONSTRAINT IF EXISTS bar;
        #ALTER TABLE foo ADD CONSTRAINT bar ...;
        #'ALTER TABLE campaigns DROP COLUMN IF EXISTS zipchk;'
        #'ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS zipchk;'
        #'ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5);'

    def defineTable(self):
        self.indices = []
        #self.getTableColumns()

    def generateReturn(self):
        return (self.create).replace('CREATE','CREATE OR REPLACE')

    def defineType(self):
        if(self.create.find('AS ENUM') != -1):
            self.type = 'ENUM'    
        #self.getParams()

    def defineView(self):
        #self.getParams()
        self.cols = []
count = 0
def newOBJ(nf):
    global count
    count += 1
    if((nf.type == 'FUNCTION')or(nf.type == 'TRIGGER')):
        global fnddeps_allfxns
        for o in fnddeps_allfxns:
            if((nf.schema==nf.schema) and (nf.name == o.name)):
                return False
        if(nf.name in enginelist):
            nf.engine_use = True
            nf.in_use = True
        fnddeps_allfxns.append(nf)
    elif(nf.type == 'VIEW'):
        global fnddeps_allviews
        for v in views:
            if((nf.schema==nf.schema) and (nf.name == o.name)):
                return False
        fnddeps_allviews.append(nf)
    return True


dpObjects = []
# create DATAchunk counters
stripName = re.compile('(.*--?)\n')
stripParams = re.compile('(\(.*?\))[;|$|\sRETURNS]',re.DOTALL)
# THE from-dump object class
#directory in app where all services are



objSplit = re.compile('--\\n--')
defLine = re.compile('(.*?)\n--')
defSplit = re.compile('\:\s(.*?).[$|\n|;]')

fnddeps = []
fnddeps_allfxns = []
fnddeps_allviews = []
service_list = []
safelist = []
enginelist = []

with open(schema_only_dbdump,encoding="utf-8") as fp:    
    contents = fp.read()
    for entry in objSplit.split(contents):
        if(len(entry)>1):
            dpObjects.append(dpObj(entry))
with open('data\\safe_list.csv',encoding="utf-8") as ff:
    slist = ff.read()
    for sf in re.split(r'\n*', slist):        
        if(len(sf)>1):
            safelist.append(sf) 

with open('data\\engine_sprocs.csv',encoding="utf-8") as ff: 
    elist = ff.read()
    for ef in re.split(r'\n*', elist):        
        if(len(ef)>1):
            enginelist.append(ef) 

for dpO in dpObjects:
    #if((dpO.type != 'COMMENT') and (dpO.type != 'OPERATOR') and (dpO.schema != 'pg_catalog')):
    if((dpO.type == 'TABLE') or (dpO.type == 'TRIGGER') or (dpO.type == 'TYPE') or (dpO.type == 'FUNCTION')or (dpO.type == 'VIEW') or (dpO.type == 'ENUM')):
        if(((dpO.schema == 'reporting') and (dpO.name.find('rollup') > -1)) and not((dpO.schema+'.'+dpO.name) in safelist)):
            fnddeps.append(dpO)

for dob in dpObjects:
    dob_def = dob.definition.lower()
    for i in range(0,(len(fnddeps)-1)):
        if((dob.name != fnddeps[i].name) and ((dob_def.find(fnddeps[i].schema+'.'+fnddeps[i].name)>-1)or(dob_def.find(fnddeps[i].name)>-1))):
            if((dob.type == 'TABLE') or (dob.type == 'TRIGGER') or (dob.type == 'TYPE') or (dob.type == 'FUNCTION') or (dob.type == 'VIEW') or (dob.type == 'ENUM')):
                newStr = ','+dob.type+','+dob.schema+','+dob.name
                if(not(newStr in fnddeps[i].dependants)):
                    fnddeps[i].dependants.append(newStr)
                newOBJ(dob)                    

for ed in fnddeps:
    for i in range(0,(len(fnddeps_allfxns)-1)):
        fxndef = fnddeps_allfxns[i].definition.lower()
        if((ed.name != fnddeps_allfxns[i].name) and ((fxndef.find(ed.schema+'.'+ed.name)>-1)or(fxndef.find(ed.name)>-1))):
            newStr = ','+ed.type+','+ed.schema+','+ed.name
            if(not(newStr in fnddeps_allfxns[i].dependencies)):
                fnddeps_allfxns[i].dependencies.append(newStr)

getServices();
engServ =[]
for alls in service_list:
    edep = False
    for i in range(0,(len(fnddeps)-1)):
        if(alls.table == fnddeps[i].name):
            newStr_Table=',SERVICE,'+alls.fl+ ',table,'+alls.table
            if(not(newStr_Table in fnddeps[i].dependants)):
                fnddeps[i].dependants.append(newStr_Table)
            edep = True 
        if(alls.view == fnddeps[i].name):
            newStr_View=',SERVICE,'+alls.fl+ ',view,'+alls.view
            if(not(newStr_View in fnddeps[i].dependants)):
                fnddeps[i].dependants.append(newStr_View)
            edep = True       
        if ((edep) and not(alls in engServ)):
            engServ.append(alls)
    edep = False
    for i in range(0,(len(fnddeps_allfxns)-1)):
        if((alls.isSproc) and (fnddeps_allfxns[i].name.find(alls.name) > -1)):
            for fxn in alls.sproc_names:
                    if(fnddeps_allfxns[i].name==fxn):
                        fnddeps_allfxns[i].dependencies.append(',SERVICE,'+alls.fl+ ',view,'+fxn)
                        edep = True
        if ((edep) and not(alls in engServ)):
            engServ.append(alls)

fo = open('data\\by_tbl.csv', "w")
for ed in fnddeps:
    if(len(ed.dependants)>0):
        ed_deps = ed.type+','+ed.schema+','+ed.name+'\n'
        ed_deps += '\n'.join(ed.dependants) +'\n'
        fo.write(ed_deps)
fo.close()

f6 = open('data\\by_fxn.csv', "w")
for fxn in fnddeps_allfxns:
    if(len(fxn.dependencies)>0):
        fxn_deps = fxn.type+','+fxn.schema+','+fxn.name+'\n'
        fxn_deps += '\n'.join(fxn.dependencies) +'\n'
        f6.write(fxn_deps)
f6.close()

f1 = open('data\\fxns.csv', "w")
dfxns=''
fnddeps_allfxns=sorted(fnddeps_allfxns, key=lambda x: x.schema, reverse=False)
print(str(len(fnddeps_allfxns)))
for fxn in fnddeps_allfxns: 
    if(len(fxn.dependencies)>0):
        dfxns += fxn.schema + ',' + fxn.name  + '\n'
f1.write(dfxns)
f1.close()

f3 = open('data\\tbls.csv', "w")
dtbls=''
for tbl in sorted(fnddeps, key=lambda x: x.schema, reverse=False):  
    if((tbl.type == 'TABLE') or (tbl.type == 'VIEW')):
        dtbls += tbl.schema + ',' + tbl.name  + '\n'
f3.write(dtbls)
f3.close()

f3 = open('data\\views.csv', "w")
dtbls=''
for tbl in sorted(fnddeps_allviews, key=lambda x: x.schema, reverse=False):  
    if((tbl.type == 'TABLE') or (tbl.type == 'VIEW')):
        dtbls += tbl.schema + ',' + tbl.name  + '\n'
f3.write(dtbls)
f3.close()

f2 = open('data\\safe_list.csv', "w")
slstr=''
for sf in safelist:  
    slstr += sf+'\n'
f2.write(slstr)
f2.close()

fsr = open('data\\by_srv.csv', "w")
srvcs=''
for srv in engServ: 
    srvcs =''
    if (len(srv.sproc_names)>0): 
        srvcs +='\n'+'\n'.join(srv.sproc_names)
    if(len(srv.table)>0):
        srvcs +='\n'+srv.table
    if(len(srv.view)>0):
        srvcs +='\n'+srv.view
    if(len(srvcs)>0):
        srvcs ='SERVICE,'+srv.fl+','+ str(srv.in_use)+srvcs+'\n'
    fsr.write(srvcs)
fsr.close()

quit();

