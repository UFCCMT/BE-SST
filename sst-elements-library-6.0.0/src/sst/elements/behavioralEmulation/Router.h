#ifndef ROUTER_H
#define ROUTER_H

#include <vector>
#include <string>
#include <map>
#include "Layout.h"
namespace SST{
namespace BEComponent{


class DynamicRouter{
public:
    DynamicRouter(std::string topo, int o, int p, std::vector<int> cd, std::vector<int> pl, std::vector<int> ml, std::vector<int> cl) 
    {
        topology = topo;
        ordinal = o;
        parent = p;
        containerDimensions = cd;
        plusNeighbour = pl;
        minusNeighbour = ml;
        childrenList = cl;
        containerSize = 1;

        for(int i=0; i<containerDimensions.size(); i++) containerSize = containerSize*containerDimensions[i];
	
	if(topology == "tree")
	{
	  //L1
		int count=1;
		L1.push_back(count);
		
	  //L2
		for(int i=1;i<=containerDimensions[0];i++)
		{
		  count++;
		  L2.push_back(count);
		}
	  
	  //L3
	  
		for(int i=0;i<(containerDimensions[0]*containerDimensions[1]);i++)
		{
		  if(i==0)
		  {
		    count++;
		    L3.push_back(count);
		  }
		  else if(i%2==1)
		  {
		    count++;
		    L3.push_back(count);
		  }
		  else
		  {
		    count = L3[i-1] + (2*(containerDimensions[2]+containerDimensions[3]))+1;
		    L3.push_back(count);
		  }  
		}
		
	  //L4
	  
		  count = 1+ containerDimensions[0] + containerDimensions[1] + containerDimensions[2]; 
		  for(int i=0;i<(containerDimensions[0]*containerDimensions[1]);i++)
		  {
		    if(i==0)
		    {
		      L4.push_back(count);
		    }
		    else if(i%2==1)
		    {
		      count = count + containerDimensions[3] + 1;
		      L4.push_back(count);
		    }
		    else
		    {
		      count = count + containerDimensions[3] + containerDimensions[1] + 1;
		      L4.push_back(count);
		    }
		  }
		  
	  //L5
	  
		  count = containerDimensions[0] + containerDimensions[1] + containerDimensions[2] + containerDimensions[3];
		  for(int i=0;i<(containerDimensions[0]*containerDimensions[1]);i++)
		  {
		    if((i%2==0)&&(i!=0))
		      count = count + containerDimensions[1] + containerDimensions[2] + 1;
		    else if(i%2==1)
		      count = count + 2;
		    for(int j=0;j<containerDimensions[3];j++)
		    {
		      if(i==0 && j==0)
		      {
			L5.push_back(count);
		      }
		      else if(j==0)
		      {
			L5.push_back(count);
		      }
		      else
		      {
			count++;
			L5.push_back(count);
		      }
		    }
		  }
	 
	 //Link config
	 
		  count = 0;
		  for(int i=0;i<4;i++)
		  {
		    int product = 1;
		    for(int j=0;j<=i;j++)
		      product *= containerDimensions[j]; 
		    count += product;
		  }
		  count++;
		  //std::cout<<"ad"<<"\n";
		  count = count + containerDimensions[0] + containerDimensions[0] + 2 + 1;
		  for(int i=0;i<(containerDimensions[0]*containerDimensions[1]);i++)
		  {
		    if((i%2==0)&&(i!=0))
		      count = count + containerDimensions[0] + 3;
		    else if(i%2==1)
		      count = count + 3;
		    for(int j=0;j<containerDimensions[3];j++)
		    {
		      if(i==0 && j==0)
		      {
			C5.push_back(count);
		      }
		      else if(j==0)
		      {
			C5.push_back(count);
		      }
		      else
		      {
			count++;
			C5.push_back(count);
		      }
		    }
		  }
	  
	  
		
		
		
		  /*for(int i=0;i<L1.size();i++)
		    std::cout<<L1[i]<<" ";
		  std::cout<<"\n";
		  
		  for(int i=0;i<L2.size();i++)
		    std::cout<<L2[i]<<" ";
		  std::cout<<"\n";
		  
		  for(int i=0;i<L3.size();i++)
		    std::cout<<L3[i]<<" ";
		  std::cout<<"\n";
		  
		  for(int i=0;i<L4.size();i++)
		    std::cout<<L4[i]<<" ";
		  std::cout<<"\n";
		  
		  for(int i=0;i<L5.size();i++)
		    std::cout<<L5[i]<<" ";
		  std::cout<<"\n";
		  
		   for(int i=0;i<C5.size();i++)
		    std::cout<<C5[i]<<" ";
		  std::cout<<"\n";*/
		  
	  }
      }
    

    std::tuple<int, int, int> findNextHop(int, int, int);
    std::tuple<int, int, int> findNextHopWC(int, int);
    int peerTraversalForMesh(int);
    int peerTraversalForTorus(int);
    int peerTraversalForTree(int,int);

    ~DynamicRouter(){}

private:
    std::vector<int> containerDimensions, plusNeighbour, minusNeighbour, childrenList;
    int ordinal, parent, containerSize;
    std::string topology;
    std::map<int, std::tuple<int, int, int>> cache;
    std::vector<int> L1,L2,L3,L4,L5,C5;
};

class Router{
public: 
    Router(Layout* l,  std::map<std::string, std::string> p){
        policies = p;
        layout = l;
    }

    std::vector<int> path(int src, int target);
    void clear();
    ~Router(){}

private:
    std::vector<std::vector<int>> multiply (std::vector<std::vector<int>> a, int b);        
    std::vector<std::vector<int>> ident(int n, int x);
    std::vector<int> add(std::vector<int> a, std::vector<int> b);
    std::vector<int> sub(std::vector<int> a, std::vector<int> b);
    std::vector<int> torusAdd(std::vector<int> a, std::vector<int> b, std::vector<int> sizes);
    std::vector<int> torusSub(std::vector<int> a, std::vector<int> b, std::vector<int> sizes);
    std::vector<std::vector<std::vector<int>> > deltas(std::vector<int> a, std::vector<int> b); 
    std::vector<std::vector<std::vector<int>> > torusDeltas(std::vector<int> a, std::vector<int> b, std::vector<int> sizes);
    void prep(int src, int target);  
    void display(std::vector<int> l);  

    std::vector<int> forward, reverse;
    std::string netname;
    std::vector<int> netsize;
    std::map<std::string, std::string> policies;
    std::vector<std::vector<int> > across;
    //std::multimap<int, int> cache;  
    Layout* layout;
};

}
}

#endif
