'''Logic for abstracting the algorithm as send_message, prep_message  taken gathered from https://github.com/rdlester/pyfac'''


#fA(Earthquale) = p(Earthquake)
fE = dict()
fE["true"]=0.002
fE["false"]=0.998

#fB(Burglary) = p(Burglary)
fB = dict()
fB["true"]=0.001
fB["false"]=0.999

#fC(Alarm, Earthquake, Burglary) = p(Alarm|Earthquake,Burglary)
fA = dict()
fA["true true true"]=0.95
fA["true false true"]=0.94
fA["false true true"]=0.29
fA["false false true"]=0.001
fA["true true false"]=0.05
fA["true false false"]=0.06
fA["false true false"]=0.71
fA["false false false"]=0.999

#fJ(John|Alarm) = p(John|Alarm)
fJ = dict()
fJ["true true"]=0.90
fJ["false true"]=0.05
fJ["true false"]=0.10
fJ["false false"]=0.95

#fM(Mary|Alarm) = p(Mary|Alarm)
fM = dict()
fM["true true"]=0.70
fM["false true"]=0.01
fM["true false"]=0.30
fM["false false"]=0.99


def normalize(prob):
    sum=0
    for key in prob:
        sum+=prob[key]
    return 1/sum

class Graph_Node:
    
    def __init__(self,name,var,table,typ,variables):
        self.name = name
        self.var = var
        self.typ = typ
        self.factor = table
        self.inbox  = {}
        self.outbox = {}
        self.incoming = {}
        self.neighbors = set()
        self.variables = variables
        self.marginal_flag= 'true'


    def get_val(self,var):
        k = ""
        for i in var:
            k+=" "+i
        return self.factor[k.strip()]


    def product(self, node):
        
        #if table is empty
        if not node.factor :
            return self
        new_variables = []
        new_variables = list(new_variables) + list(self.variables)
        new_variables = list(new_variables) + list(node.variables)
        new_variables = set(new_variables)
        new_node = Graph_Node(self.name + "," + node.name,self.var+node.var,{},'factor',list(new_variables))
        for key_i in self.factor:
            for key_j in node.factor:
                key=key_i+" "+key_j
                #print(key)
                val=self.get_val([key_i])*node.get_val([key_j])
                new_node.factor[key]=val        
        return new_node
    
    
    def sum_over_not(self, variable):
        #print(self.name,'sum over not',self.variables,variable)
        if variable not in self.variables:
            return self
        if self.marginal_flag == 'false':
            return self
        
        value_true = 0
        value_false = 0
        index = self.variables.index(variable)
        for key in self.factor.keys():
            if key.split()[index] == "true":
                value_true += self.factor[key]
            else:
                value_false += self.factor[key]
        new_node = Graph_Node(self.name + "!" + variable,self.var,{},'factor', [variable])
        
        new_node.factor["true"]=value_true
        new_node.factor["false"]=value_false
        return new_node 
    

class Factor_Graph:
    def __init__(self):
        self.graph={}
        self.nodes={}
        self.vertices=set()
        self.nodes_flag={}
        self.q_prep = set()
        self.q_send = set()
        
    def add_edge(self,node1,node2):
        node1.neighbors.add(node2.name)
        node2.neighbors.add(node1.name)
        if node1.name not in self.graph:
            self.nodes_flag[node1.name]=-1
            self.graph[node1.name]=[]
            self.vertices.add(node1.name)
            self.nodes[node1.name]=node1
        if node2.name not in self.graph:
            self.graph[node2.name]=[]
            self.vertices.add(node2.name)
            self.nodes[node2.name]=node2
            self.nodes_flag[node2.name]=-1
        self.graph[node1.name]=node2
        self.graph[node2.name]=node1
     
        
    def prep_message(self,node_name):
        
        node=self.nodes[node_name]
        self.nodes_flag[node.name]=1
        self.q_send.add(node_name)
        prod=node
        if node.typ == "variable":
            i=0
            for desc in node.inbox:
                i+=1
                if  i== 1:
                    prod=node.inbox[desc]
                else:
                    prod=prod.product(node.inbox[desc])
        elif node.typ == "factor":
            for desc in node.inbox:
                prod=prod.product(node.inbox[desc])
            keys = set(node.inbox.keys())
            #print("Keys: ",keys)
            #print("Neighbors: ",node.neighbors)
            parent = list(node.neighbors-keys)
            for p in parent:
                p=''.join(p)
            #print("Parent: "+p)
            #print(prod.name,prod.marginal_flag)
            prod = prod.sum_over_not(p)
        out_set=node.neighbors-set(node.inbox.keys())
        for key in out_set:
            node.outbox[key]=prod
            
        node.inbox={}
        self.nodes[node_name]=node
            
            
    def send_message(self,node_name):
        
        node=self.nodes[node_name]
        for key in node.outbox:
            node_recv=self.nodes[key]
            node_recv.inbox[node_name]=node.outbox[key]
            node_recv.incoming[node_name]=node.outbox[key]
            self.nodes_flag[key]=0
            self.q_prep.add(key)
        self.nodes_flag[node.name]=-1 
        node.outbox={}
        self.nodes[node_name]=node
        
    def sum_product(self,count):
        ''' Maintain 2 queues. One for preparing messages and the other for sending. Remove nodes once done and update'''
        for i in range(count):
            print("Step:",i+1)
            print(self.q_prep)   
            for job in self.q_prep:
                    self.prep_message(job)
            self.q_prep=set()
            for job in self.q_send:
                    self.send_message(job)
            self.q_send=set()
            
        
        for key in self.vertices:
            node=self.nodes[key]
            if node.typ == 'variable':
                prod=node
                prod.marginal_flag='true'
                i=0
                for j in node.incoming:
                    i+=1
                    if  i == 1:
                        prod=node.incoming[j]
                    else:
                        prod=prod.product(node.incoming[j])
                prod=prod.sum_over_not(node.variables)
                norm=normalize(prod.factor)
                for k in prod.factor:
                    prod.factor[k]*=norm
                print(node.variables)
                print(prod.factor)
        
                    
if __name__ == '__main__':
    
    fg=Factor_Graph()
    
    fE = Graph_Node('fE','fE',fE,'factor',['xE'])
    fB = Graph_Node('fB','fB',fB,'factor',['xB'])
    fA = Graph_Node('fA','fA',fA,'factor',['xB','xE','xA'])
    fJ = Graph_Node('fJ','fJ',fJ,'factor',['xA','xJ'])
    fM = Graph_Node('fM','fM',fM,'factor',['xA','xM'])
    fE.marginal_flag='false'
    fB.marginal_flag='false'
    xE = Graph_Node('xE', 'xE',{},'variable','xE')
    xB = Graph_Node('xB', 'xB',{},'variable','xB')
    xA = Graph_Node('xA', 'xA',{},'variable','xA')
    xJ = Graph_Node('xJ', 'xJ',{},'variable','xJ')
    xM = Graph_Node('xM', 'xM',{},'variable','xM')
    xE.marginal_flag='false'
    xB.marginal_flag='false'
    xA.marginal_flag='false'
    xJ.marginal_flag='false'
    xM.marginal_flag='false'

    fg.add_edge(xE, fE)
    
    fg.add_edge(xB, fB)
    fg.add_edge(xB, fA)
    fg.add_edge(xE, fA)
    fg.add_edge(xA, fA)
    fg.add_edge(xA, fJ)
    fg.add_edge(xA, fM)
    fg.add_edge(xJ, fJ)
    fg.add_edge(xM, fM)
    

    fg.q_prep.add('fE')
    fg.q_prep.add('fB')
    fg.q_prep.add('xJ')
    fg.q_prep.add('xM')
    
    fg.sum_product(5)
    

    
